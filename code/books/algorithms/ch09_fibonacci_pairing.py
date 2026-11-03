"""Chapter 9: Fibonacci heaps (Fredman and Tarjan 1984) and pairing heaps
(Fredman, Sedgewick, Sleator and Tarjan 1986), from scratch, raced in
Dijkstra's algorithm against heapq."""
import heapq
import math
import random
import time


# ---------- Fibonacci heap ----------
class FNode:
    __slots__ = ("key", "item", "parent", "kids", "mark")

    def __init__(self, key, item):
        self.key, self.item, self.parent, self.kids, self.mark = key, item, None, [], False


class FibHeap:
    def __init__(self):
        self.roots, self.min, self.n = [], None, 0
        self.links = self.cuts = 0

    def push(self, key, item=None):        # O(1): just a new root
        x = FNode(key, item)
        self.roots.append(x)
        if self.min is None or key < self.min.key:
            self.min = x
        self.n += 1
        return x

    def pop(self):
        z = self.min
        self.roots.remove(z)               # (a linked list makes this O(1))
        for c in z.kids:                   # children become roots
            c.parent, c.mark = None, False
            self.roots.append(c)
        self.n -= 1
        self._consolidate()
        return z.key, z.item

    def _consolidate(self):
        by_degree = {}
        for x in self.roots:
            while len(x.kids) in by_degree:     # link equal degrees
                y = by_degree.pop(len(x.kids))
                if y.key < x.key:
                    x, y = y, x
                x.kids.append(y)
                y.parent = x
                y.mark = False
                self.links += 1
            by_degree[len(x.kids)] = x
        self.roots = list(by_degree.values())
        self.min = min(self.roots, key=lambda r: r.key) if self.roots else None

    def decrease_key(self, x, key):
        x.key = key
        p = x.parent
        if p is not None and x.key < p.key:
            self._cut(x)
            while p.parent is not None:          # cascading cut
                if not p.mark:
                    p.mark = True
                    break
                q = p.parent
                self._cut(p)
                p = q
        if x.key < self.min.key:
            self.min = x

    def _cut(self, x):
        x.parent.kids.remove(x)
        x.parent, x.mark = None, False
        self.roots.append(x)
        self.cuts += 1

    def max_degree(self):
        best, stack = 0, list(self.roots)
        while stack:
            x = stack.pop()
            best = max(best, len(x.kids))
            stack.extend(x.kids)
        return best


# ---------- pairing heap ----------
class PNode:
    __slots__ = ("key", "item", "child", "sib", "prev")

    def __init__(self, key, item):
        self.key, self.item = key, item
        self.child = self.sib = self.prev = None   # prev: parent or left sibling


def meld(a, b):
    if a is None:
        return b
    if b is None:
        return a
    if b.key < a.key:
        a, b = b, a
    b.prev, b.sib = a, a.child             # b becomes a's first child
    if a.child:
        a.child.prev = b
    a.child, a.sib, a.prev = b, None, None
    return a


class PairingHeap:
    def __init__(self):
        self.root, self.n = None, 0

    def push(self, key, item=None):
        x = PNode(key, item)
        self.root = meld(self.root, x)
        self.n += 1
        return x

    def decrease_key(self, x, key):
        x.key = key
        if x is self.root:
            return
        if x.prev.child is x:              # detach x with its subtree
            x.prev.child = x.sib
        else:
            x.prev.sib = x.sib
        if x.sib:
            x.sib.prev = x.prev
        x.sib = x.prev = None
        self.root = meld(self.root, x)

    def pop(self):
        r = self.root
        kids, c = [], r.child
        while c:
            nxt = c.sib
            c.sib = c.prev = None
            kids.append(c)
            c = nxt
        pairs = [meld(kids[i], kids[i + 1] if i + 1 < len(kids) else None)
                 for i in range(0, len(kids), 2)]       # pass 1: left to right
        t = None
        for p in reversed(pairs):                       # pass 2: right to left
            t = meld(p, t)
        self.root = t
        self.n -= 1
        return r.key, r.item


def dijkstra(adj, s, Heap):
    dist = [math.inf] * len(adj)
    dist[s] = 0
    h, handle = Heap(), {}
    handle[s] = h.push(0, s)
    done = [False] * len(adj)
    while h.n:
        d, u = h.pop()
        done[u] = True
        for v, w in adj[u]:
            if not done[v] and d + w < dist[v]:
                dist[v] = d + w
                if v in handle:
                    h.decrease_key(handle[v], d + w)
                else:
                    handle[v] = h.push(d + w, v)
    return dist


def dijkstra_heapq(adj, s):
    dist = [math.inf] * len(adj)
    dist[s] = 0
    pq = [(0, s)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(pq, (d + w, v))
    return dist


if __name__ == "__main__":
    f = FibHeap()
    nodes = {k: f.push(k) for k in [7, 3, 18, 52, 38, 39, 41, 23, 17, 24, 26, 46, 35]}
    print("13 pushes: roots", len(f.roots), "min", f.min.key)
    print("pop ->", f.pop()[0], "| roots after consolidate:",
          sorted((r.key, len(r.kids)) for r in f.roots), "| links", f.links)
    f.decrease_key(nodes[46], 15)
    f.decrease_key(nodes[35], 5)
    print("decrease 46->15, 35->5: roots", sorted(r.key for r in f.roots),
          "| min", f.min.key, "| cuts", f.cuts)

    random.seed(1984)
    n = 50000
    f, p = FibHeap(), PairingHeap()
    keys = [random.random() for _ in range(n)]
    hf = [f.push(k) for k in keys]
    hp = [p.push(k) for k in keys]
    f.pop(); p.pop()
    phi = (1 + 5 ** 0.5) / 2
    print(f"Fibonacci heap, n = {n}: max degree after one pop {f.max_degree()}, "
          f"bound log_phi n = {math.log(n, phi):.1f}")
    for i in random.sample(range(n), 10000):
        if hf[i].parent is not None or hf[i] in f.roots:
            new = hf[i].key / 2
            f.decrease_key(hf[i], new)
            p.decrease_key(hp[i], new)
    a = [f.pop()[0] for _ in range(2000)]
    b = [p.pop()[0] for _ in range(2000)]
    print("2000 pops agree after 10000 decrease-keys:", a == b == sorted(a))

    n, m = 30000, 150000
    adj = [[] for _ in range(n)]
    for _ in range(m):
        u, v, w = random.randrange(n), random.randrange(n), random.randint(1, 1000)
        adj[u].append((v, w))
        adj[v].append((u, w))
    t0 = time.perf_counter(); d0 = dijkstra_heapq(adj, 0); t1 = time.perf_counter()
    d1 = dijkstra(adj, 0, FibHeap); t2 = time.perf_counter()
    d2 = dijkstra(adj, 0, PairingHeap); t3 = time.perf_counter()
    print("all three agree:", d0 == d1 == d2)
    print(f"Dijkstra, n = {n}, m = {m}: heapq {t1 - t0:.2f} s, "
          f"Fibonacci {t2 - t1:.2f} s, pairing {t3 - t2:.2f} s")
