"""Chapter 13: speed-ups. Hirschberg's linear-space LCS, Knuth's optimization,
divide-and-conquer optimization, and the convex hull trick, each checked against the plain DP."""
import random

# ---------- Hirschberg: an actual LCS string in O(mn) time and O(n) space ----------

def lcs_row(x, y):
    """Last row of the LCS table of x and y, using two rows only."""
    prev = [0] * (len(y) + 1)
    for a in x:
        cur = [0]
        for j, b in enumerate(y, 1):
            cur.append(prev[j - 1] + 1 if a == b else max(prev[j], cur[j - 1]))
        prev = cur
    return prev


def hirschberg(x, y):
    if not x or not y:
        return ""
    if len(x) == 1:
        return x if x in y else ""
    mid = len(x) // 2
    left = lcs_row(x[:mid], y)                       # forward scores for the top half
    right = lcs_row(x[mid:][::-1], y[::-1])          # backward scores for the bottom half
    k = max(range(len(y) + 1), key=lambda j: left[j] + right[len(y) - j])
    return hirschberg(x[:mid], y[:k]) + hirschberg(x[mid:], y[k:])


def lcs_length(x, y):
    return lcs_row(x, y)[-1]

# ---------- Knuth's optimization for optimal binary search trees ----------

def obst(freq, knuth):
    """Cost of the best BST for keys with these frequencies (cost = sum freq * depth, root depth 1)."""
    n = len(freq)
    pre = [0]
    for f in freq:
        pre.append(pre[-1] + f)
    e = [[0] * (n + 1) for _ in range(n + 1)]       # e[i][j]: keys i..j-1
    root = [[0] * (n + 1) for _ in range(n + 1)]
    steps = 0
    for i in range(n):
        e[i][i + 1], root[i][i + 1] = freq[i], i
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length
            lo, hi = (root[i][j - 1], root[i + 1][j]) if knuth else (i, j - 1)
            best = None
            for r in range(lo, hi + 1):
                steps += 1
                c = e[i][r] + e[r + 1][j]
                if best is None or c < best:
                    best, root[i][j] = c, r
            e[i][j] = best + pre[j] - pre[i]
    return e[0][n], steps

# ---------- divide-and-conquer optimization ----------

def partition_cost_plain(a, k):
    """Split a into k contiguous groups minimising the sum of (group sum)^2."""
    n = len(a)
    pre = [0]
    for v in a:
        pre.append(pre[-1] + v)
    INF = float("inf")
    dp = [0] + [INF] * n
    for _ in range(k):
        new = [INF] * (n + 1)
        for i in range(1, n + 1):
            new[i] = min(dp[j] + (pre[i] - pre[j]) ** 2 for j in range(i))
        dp = new
    return dp[n]


def partition_cost_dc(a, k):
    n = len(a)
    pre = [0]
    for v in a:
        pre.append(pre[-1] + v)
    INF = float("inf")
    dp = [0] + [INF] * n

    def solve(new, lo, hi, opt_lo, opt_hi):
        if lo > hi:
            return
        mid = (lo + hi) // 2
        best, best_j = INF, opt_lo
        for j in range(opt_lo, min(mid - 1, opt_hi) + 1):
            c = dp[j] + (pre[mid] - pre[j]) ** 2
            if c < best:
                best, best_j = c, j
        new[mid] = best
        solve(new, lo, mid - 1, opt_lo, best_j)       # the best split point only moves right
        solve(new, mid + 1, hi, best_j, opt_hi)
    for _ in range(k):
        new = [INF] * (n + 1)
        solve(new, 1, n, 0, n - 1)
        dp = new
    return dp[n]

# ---------- convex hull trick ----------

def frog_plain(x, C):
    """dp[i] = min over j < i of dp[j] + (x[i] - x[j])^2 + C, dp[0] = 0."""
    dp = [0] * len(x)
    for i in range(1, len(x)):
        dp[i] = min(dp[j] + (x[i] - x[j]) ** 2 + C for j in range(i))
    return dp[-1]


def frog_hull(x, C):
    """Each j gives a line y = m*t + b with m = -2 x[j], b = dp[j] + x[j]^2; query at t = x[i]."""
    from collections import deque
    lines = deque()

    def bad(l1, l2, l3):                       # l2 is never the minimum once l3 arrives
        return (l3[1] - l1[1]) * (l1[0] - l2[0]) <= (l2[1] - l1[1]) * (l1[0] - l3[0])
    dp = [0] * len(x)
    lines.append((-2 * x[0], dp[0] + x[0] ** 2))
    for i in range(1, len(x)):
        t = x[i]
        while len(lines) >= 2 and lines[1][0] * t + lines[1][1] <= lines[0][0] * t + lines[0][1]:
            lines.popleft()                    # queries increase, so the front line retires
        m, b = lines[0]
        dp[i] = m * t + b + t * t + C
        new = (-2 * x[i], dp[i] + x[i] ** 2)   # slopes decrease as x increases
        while len(lines) >= 2 and bad(lines[-2], lines[-1], new):
            lines.pop()
        lines.append(new)
    return dp[-1]


def is_subsequence(s, t):
    it = iter(t)
    return all(c in it for c in s)


if __name__ == "__main__":
    random.seed(8)
    x = "".join(random.choice("ACGT") for _ in range(300))
    y = "".join(random.choice("ACGT") for _ in range(300))
    h = hirschberg(x, y)
    print("Hirschberg LCS length", len(h), "| full-table length", lcs_length(x, y),
          "| common subsequence of both:", is_subsequence(h, x) and is_subsequence(h, y))

    freq = [random.randint(1, 50) for _ in range(120)]
    c1, s1 = obst(freq, knuth=False)
    c2, s2 = obst(freq, knuth=True)
    print(f"optimal BST, 120 keys: plain cost {c1} in {s1} inner steps; Knuth cost {c2} in {s2} steps")

    a = [random.randint(1, 20) for _ in range(200)]
    print("partition 200 numbers into 6 groups: plain", partition_cost_plain(a, 6),
          " divide and conquer", partition_cost_dc(a, 6))

    xs = sorted(random.sample(range(1, 10 ** 6), 2000))
    print("stops on a route, first 400: plain", frog_plain(xs[:400], 10 ** 7),
          " hull", frog_hull(xs[:400], 10 ** 7), "| hull on all 2000:", frog_hull(xs, 10 ** 7))

    ok = True
    for _ in range(100):
        u = "".join(random.choice("AB") for _ in range(random.randint(0, 25)))
        v = "".join(random.choice("AB") for _ in range(random.randint(0, 25)))
        g = hirschberg(u, v)
        ok &= len(g) == lcs_length(u, v) and is_subsequence(g, u) and is_subsequence(g, v)
        f = [random.randint(1, 30) for _ in range(random.randint(1, 15))]
        ok &= obst(f, True)[0] == obst(f, False)[0]
        b = [random.randint(1, 9) for _ in range(random.randint(3, 20))]
        k = random.randint(1, 3)
        ok &= partition_cost_plain(b, k) == partition_cost_dc(b, k)
        z = sorted(random.sample(range(1, 500), random.randint(2, 30)))
        ok &= frog_plain(z, 300) == frog_hull(z, 300)
    print("100 random tests of all four speed-ups against the plain DP passed:", ok)
