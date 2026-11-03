# Chapter 18: sampling-based motion planning from scratch. A disc robot among circular rocks:
# configuration space by inflating obstacles, an RRT (LaValle 1998) and a PRM (Kavraki et al. 1996).
import heapq
import math
import numpy as np

ROBOT_R = 0.3
ROCKS = [((5.0, 5.0), 1.5), ((3.0, 7.0), 1.0), ((7.0, 3.0), 1.0), ((7.5, 7.5), 0.8), ((2.5, 3.5), 0.8)]
C_OBS = [(np.array(c), r + ROBOT_R) for c, r in ROCKS]   # C-space: the robot is a point, rocks grow by its radius
START, GOAL = np.array([1.0, 1.0]), np.array([9.0, 9.0])


def free_point(p):
    return 0 <= p[0] <= 10 and 0 <= p[1] <= 10 and all(np.linalg.norm(p - c) > r for c, r in C_OBS)


def free_segment(a, b):
    """Exact test: the segment misses every inflated rock if its closest point to each centre is outside."""
    ab = b - a
    L2 = float(ab @ ab)
    for c, r in C_OBS:
        t = 0.0 if L2 == 0 else min(1.0, max(0.0, float((c - a) @ ab) / L2))
        if np.linalg.norm(a + t * ab - c) <= r:
            return False
    return True


def path_length(path):
    return sum(np.linalg.norm(path[i + 1] - path[i]) for i in range(len(path) - 1))


def rrt(rng, step=0.5, goal_bias=0.05, max_iter=5000):
    nodes, parent = [START], [-1]
    for it in range(1, max_iter + 1):
        q = GOAL if rng.random() < goal_bias else rng.uniform(0, 10, 2)    # random target
        d = np.linalg.norm(np.array(nodes) - q, axis=1)
        i = int(d.argmin())                                               # nearest tree node
        new = q if d[i] <= step else nodes[i] + step * (q - nodes[i]) / d[i]  # steer one step toward it
        if not free_point(new) or not free_segment(nodes[i], new):
            continue
        nodes.append(new); parent.append(i)
        if np.linalg.norm(new - GOAL) <= step and free_segment(new, GOAL):
            nodes.append(GOAL); parent.append(len(nodes) - 2)
            path, k = [], len(nodes) - 1
            while k != -1:
                path.append(nodes[k]); k = parent[k]
            return path[::-1], nodes, parent, it
    return None, nodes, parent, max_iter


def shortcut(path, rng, tries=200):
    path = list(path)
    for _ in range(tries):                        # replace a stretch by a straight segment when it is free
        if len(path) < 3:
            break
        i, j = sorted(rng.choice(len(path), 2, replace=False))
        if j > i + 1 and free_segment(path[i], path[j]):
            path = path[:i + 1] + path[j:]
    return path


def prm(rng, n=300, k=10):
    pts = [START, GOAL]
    while len(pts) < n + 2:
        p = rng.uniform(0, 10, 2)
        if free_point(p):
            pts.append(p)
    P = np.array(pts)
    adj = [[] for _ in pts]
    seen = set()
    for i in range(len(pts)):                     # connect each sample to its k nearest, if the segment is free
        d = np.linalg.norm(P - P[i], axis=1)
        for j in map(int, np.argsort(d)[1:k + 1]):
            if (min(i, j), max(i, j)) not in seen and free_segment(P[i], P[j]):
                seen.add((min(i, j), max(i, j)))
                adj[i].append((j, d[j])); adj[j].append((i, d[j]))
    edges = len(seen)
    dist, prev, pq = {0: 0.0}, {0: -1}, [(0.0, 0)]   # Dijkstra from START (index 0) to GOAL (index 1)
    while pq:
        du, u = heapq.heappop(pq)
        if u == 1:
            break
        if du > dist[u]:
            continue
        for v, w in adj[u]:
            if du + w < dist.get(v, math.inf):
                dist[v], prev[v] = du + w, u
                heapq.heappush(pq, (du + w, v))
    if 1 not in dist:
        return None, edges
    path, u = [], 1
    while u != -1:
        path.append(P[u]); u = prev[u]
    return path[::-1], edges


if __name__ == "__main__":
    print(f"straight-line distance start -> goal: {np.linalg.norm(GOAL - START):.3f} (blocked: "
          f"{not free_segment(START, GOAL)})")
    rng = np.random.default_rng(1)
    path, nodes, parent, iters = rrt(rng)
    print(f"\n1. one RRT run (seed 1): {iters} iterations, {len(nodes)} tree nodes, path of {len(path)} points")
    print(f"   path length {path_length(path):.3f}; after shortcutting {path_length(shortcut(path, rng)):.3f}")

    print("\n2. RRT over 20 seeds")
    lens, sizes = [], []
    for s in range(20):
        p, nd, _, _ = rrt(np.random.default_rng(100 + s))
        if p is not None:
            lens.append(path_length(p)); sizes.append(len(nd))
    print(f"   solved {len(lens)} of 20; tree size mean {np.mean(sizes):.0f}; "
          f"path length mean {np.mean(lens):.2f}, min {min(lens):.2f}, max {max(lens):.2f}")

    print("\n3. PRM: 300 free samples, each tried against its 10 nearest neighbours")
    for s in range(3):
        p, e = prm(np.random.default_rng(200 + s))
        print(f"   seed {200 + s}: {e} free edges, shortest roadmap path {path_length(p):.3f} with {len(p)} points")
