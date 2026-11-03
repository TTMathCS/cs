# Chapter 24: online algorithms.  Ski rental (deterministic and randomized)
# and paging: LRU, FIFO and Belady's offline optimum.
from collections import OrderedDict, deque
import random


# ---------- ski rental: renting costs 1 a day, buying costs B ----------
def cost_buy_on_day(t, days, B):
    """Rent until day t-1, buy on day t (if the season lasts that long)."""
    return days if days < t else (t - 1) + B


def worst_ratio_deterministic(t, B, horizon=200):
    return max(cost_buy_on_day(t, d, B) / min(d, B) for d in range(1, horizon))


B = 10
print(f"ski rental, B = {B}: worst-case ratio of 'buy on day t'")
for t in (1, 5, 10, 11, 15, 20):
    print(f"  t = {t:2d}: {worst_ratio_deterministic(t, B):.3f}")
print(f"  best deterministic: t = B gives 2 - 1/B = {2 - 1 / B:.3f}")

# Randomized: buy on day t with probability proportional to ((B-1)/B)^(B-t).
w = [((B - 1) / B) ** (B - t) for t in range(1, B + 1)]
probs = [x / sum(w) for x in w]
worst = max(sum(p * cost_buy_on_day(t, d, B) for t, p in zip(range(1, B + 1), probs))
            / min(d, B) for d in range(1, 200))
e = 2.718281828459045
print(f"  randomized: worst expected ratio {worst:.3f} (limit e/(e-1) = {e / (e - 1):.3f})")
print()


# ---------- paging with a cache of k pages ----------
def lru(requests, k):
    cache, misses = OrderedDict(), 0
    for r in requests:
        if r in cache:
            cache.move_to_end(r)                    # most recently used at the end
        else:
            misses += 1
            if len(cache) == k:
                cache.popitem(last=False)           # evict least recently used
            cache[r] = True
    return misses


def fifo(requests, k):
    cache, order, misses = set(), deque(), 0
    for r in requests:
        if r not in cache:
            misses += 1
            if len(cache) == k:
                cache.discard(order.popleft())
            cache.add(r)
            order.append(r)
    return misses


def belady(requests, k):
    """Offline optimum: evict the page whose next request is farthest away."""
    n = len(requests)
    next_use = [0] * n
    last = {}
    for i in range(n - 1, -1, -1):
        next_use[i] = last.get(requests[i], n)
        last[requests[i]] = i
    cache, misses = {}, 0                           # page -> index of its next use
    for i, r in enumerate(requests):
        if r not in cache:
            misses += 1
            if len(cache) == k:
                victim = max(cache, key=cache.get)
                del cache[victim]
        cache[r] = next_use[i]
    return misses


def marking(requests, k, rng):
    """Randomized marking: on a miss evict a random unmarked page."""
    cache, marked, misses = set(), set(), 0
    for r in requests:
        if r not in cache:
            misses += 1
            if len(cache) == k:
                if marked >= cache:                 # all marked: a new phase
                    marked = set()
                cache.discard(rng.choice(sorted(cache - marked)))
            cache.add(r)
        marked.add(r)
    return misses


k = 4
cyclic = [i % (k + 1) for i in range(100)]          # k+1 pages in a loop
rng = random.Random(24)
local = []
page = 0
for _ in range(2000):                               # a walk with locality
    page = max(0, page + rng.choice([-1, 0, 1, 1, -1, 0, 0]))
    local.append(page % 12)
print(f"paging with k = {k} frames      LRU  FIFO  marking  OPT")
for title, seq in [("cyclic over k+1 pages (100)", cyclic), ("walk with locality (2000)", local)]:
    print(f"  {title:28s} {lru(seq, k):4d}  {fifo(seq, k):4d}  "
          f"{marking(seq, k, random.Random(1)):7d}  {belady(seq, k):3d}")
