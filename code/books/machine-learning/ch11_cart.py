"""Chapter 11.2: CART from scratch. Binary splits on numeric features chosen by Gini
(classification) or squared error (regression), grown greedily, then pruned by
cost-complexity (weakest-link) pruning. The other Chapter 11 programs import this file."""
import numpy as np


class Node:
    def __init__(self, value, n, impurity_sum):
        self.value = value             # prediction: class-count vector, or mean
        self.n = n                     # training points that reach this node
        self.cost = impurity_sum       # n * impurity (Gini) or the sum of squared errors
        self.feature = None            # None means leaf
        self.threshold = self.left = self.right = None
        self.gain = 0.0                # decrease in cost from splitting here


def best_split(X, y, idx, task, n_classes, features):
    """Best (feature, threshold, cost after split) over all features and cut points,
    in O(d n log n) by sorting each feature once and sweeping with running sums."""
    best = (None, None, np.inf)
    n = len(idx)
    for f in features:
        order = idx[np.argsort(X[idx, f], kind="stable")]
        xs = X[order, f]
        if task == "classify":
            onehot = np.eye(n_classes)[y[order]]
            left = np.cumsum(onehot, axis=0)[:-1]          # class counts left of each cut
            right = left[-1] + onehot[-1] - left
            nl = np.arange(1, n)[:, None]
            nr = n - nl
            cost = (nl[:, 0] - (left ** 2).sum(1) / nl[:, 0]) + (nr[:, 0] - (right ** 2).sum(1) / nr[:, 0])
        else:
            ys = y[order]
            s, s2 = np.cumsum(ys)[:-1], np.cumsum(ys ** 2)[:-1]
            S, S2 = ys.sum(), (ys ** 2).sum()
            nl = np.arange(1, n)
            cost = (s2 - s ** 2 / nl) + ((S2 - s2) - (S - s) ** 2 / (n - nl))
        valid = xs[1:] > xs[:-1]                           # cut only between distinct values
        if not valid.any():
            continue
        cost = np.where(valid, cost, np.inf)
        k = int(np.argmin(cost))
        if cost[k] < best[2]:
            best = (f, (xs[k] + xs[k + 1]) / 2, cost[k])
    return best


def node_stats(y, idx, task, n_classes):
    if task == "classify":
        counts = np.bincount(y[idx], minlength=n_classes).astype(float)
        return counts, len(idx) - (counts ** 2).sum() / len(idx)     # n * Gini
    m = y[idx].mean()
    return m, ((y[idx] - m) ** 2).sum()


def grow(X, y, idx, task, n_classes=2, max_depth=50, min_leaf=1, max_features=None, rng=None, depth=0):
    value, cost = node_stats(y, idx, task, n_classes)
    node = Node(value, len(idx), cost)
    if depth >= max_depth or len(idx) < 2 * min_leaf or cost <= 1e-12:
        return node
    d = X.shape[1]
    feats = range(d) if max_features is None else rng.choice(d, max_features, replace=False)
    f, t, c = best_split(X, y, idx, task, n_classes, feats)
    if f is None:
        return node
    go_left = X[idx, f] <= t
    if go_left.sum() < min_leaf or (~go_left).sum() < min_leaf:
        return node
    node.feature, node.threshold, node.gain = f, t, cost - c
    node.left = grow(X, y, idx[go_left], task, n_classes, max_depth, min_leaf, max_features, rng, depth + 1)
    node.right = grow(X, y, idx[~go_left], task, n_classes, max_depth, min_leaf, max_features, rng, depth + 1)
    return node


def predict_one(node, x):
    while node.feature is not None:
        node = node.left if x[node.feature] <= node.threshold else node.right
    return node.value


def predict(node, X, task):
    """Route all rows down the tree at once: each node splits its index set in two."""
    out = np.empty(len(X)) if task == "regress" else np.empty(len(X), dtype=int)
    stack = [(node, np.arange(len(X)))]
    while stack:
        t, idx = stack.pop()
        if t.feature is None:
            out[idx] = t.value if task == "regress" else np.argmax(t.value)
            continue
        go = X[idx, t.feature] <= t.threshold
        stack += [(t.left, idx[go]), (t.right, idx[~go])]
    return out


def leaves(node):
    return 1 if node.feature is None else leaves(node.left) + leaves(node.right)


def depth(node):
    return 0 if node.feature is None else 1 + max(depth(node.left), depth(node.right))


def errors(node):
    """Training misclassifications: in a leaf, n minus its majority count."""
    if node.feature is None:
        return node.n - node.value.max()
    return errors(node.left) + errors(node.right)


def weakest_link(node, N):
    """Internal node minimising g = (R(node as leaf) - R(subtree)) / (leaves - 1)."""
    best = (np.inf, None)
    stack = [node]
    while stack:
        t = stack.pop()
        if t.feature is None:
            continue
        g = ((t.n - t.value.max()) - errors(t)) / N / (leaves(t) - 1)
        if g < best[0]:
            best = (g, t)
        stack += [t.left, t.right]
    return best


def make_data(n, rng, flip=0.15):
    """Two features in [0,1]^2; class 1 inside a disc or in the top-right corner; 15% labels flipped."""
    X = rng.uniform(0, 1, (n, 2))
    y = (((X[:, 0] - 0.35) ** 2 + (X[:, 1] - 0.4) ** 2 < 0.06) | ((X[:, 0] > 0.7) & (X[:, 1] > 0.7))).astype(int)
    flip_mask = rng.random(n) < flip
    return X, np.where(flip_mask, 1 - y, y)


if __name__ == "__main__":
    rng = np.random.default_rng(6)
    Xtr, ytr = make_data(400, rng)
    Xva, yva = make_data(400, rng)
    Xte, yte = make_data(2000, rng)

    print("Classification tree on 400 noisy points (15% of labels flipped)")
    print("  max depth  leaves  train acc  valid acc")
    for md in [1, 2, 3, 4, 6, 8, 12, 50]:
        t = grow(Xtr, ytr, np.arange(400), "classify", max_depth=md)
        print(f"  {md:9d}  {leaves(t):6d}  {np.mean(predict(t, Xtr, 'classify') == ytr):9.3f}"
              f"  {np.mean(predict(t, Xva, 'classify') == yva):9.3f}")

    print("\nCost-complexity pruning of the full tree (weakest link first)")
    tree = grow(Xtr, ytr, np.arange(400), "classify")
    print("  leaves  train acc  valid acc   pruned next at alpha")
    seq = []
    while True:
        tr = np.mean(predict(tree, Xtr, "classify") == ytr)
        va = np.mean(predict(tree, Xva, "classify") == yva)
        seq.append((leaves(tree), va))
        if tree.feature is None:
            break
        g, node = weakest_link(tree, 400)
        if len(seq) % 5 == 1 or leaves(tree) <= 12:
            print(f"  {leaves(tree):6d}  {tr:9.3f}  {va:9.3f}   {g:.4f}")
        node.feature = None                      # prune: the node becomes a leaf
    print(f"       1  {np.mean(predict(tree, Xtr, 'classify') == ytr):9.3f}  {seq[-1][1]:9.3f}   (the root alone)")
    best_leaves = max(seq, key=lambda s: (s[1], -s[0]))[0]
    print(f"best validation accuracy at {best_leaves} leaves")
    tree = grow(Xtr, ytr, np.arange(400), "classify")
    while leaves(tree) > best_leaves:
        weakest_link(tree, 400)[1].feature = None
    print(f"pruned tree: test accuracy {np.mean(predict(tree, Xte, 'classify') == yte):.3f}"
          f" (the best possible is about 0.85, the share of unflipped labels)")
    full = grow(Xtr, ytr, np.arange(400), "classify")
    print(f"unpruned tree: test accuracy {np.mean(predict(full, Xte, 'classify') == yte):.3f}")

    print("\nThe pruned tree as rules:")

    def show(node, indent="  "):
        if node.feature is None:
            print(f"{indent}predict {int(np.argmax(node.value))}  ({int(node.value.max())}/{node.n})")
            return
        print(f"{indent}if x{node.feature} <= {node.threshold:.3f}:")
        show(node.left, indent + "    ")
        print(f"{indent}else:")
        show(node.right, indent + "    ")

    show(tree)

    print("\nRegression tree on y = sin(4x) + noise, 200 points")
    x = rng.uniform(0, 1, (200, 1))
    yr = np.sin(4 * x[:, 0]) + rng.normal(0, 0.2, 200)
    xt = rng.uniform(0, 1, (1000, 1))
    yt = np.sin(4 * xt[:, 0]) + rng.normal(0, 0.2, 1000)
    for md in [1, 2, 3, 5, 8]:
        t = grow(x, yr, np.arange(200), "regress", max_depth=md)
        print(f"  depth {md}: {leaves(t):3d} leaves, test MSE {np.mean((predict(t, xt, 'regress') - yt) ** 2):.4f}")
