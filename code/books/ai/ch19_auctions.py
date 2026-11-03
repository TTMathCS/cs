# Chapter 19: auctions. Truthfulness of the second-price (Vickrey 1961) auction checked,
# bid shading in the first-price auction, revenue equivalence simulated, and a tiny VCG example.
from itertools import product
import numpy as np

rng = np.random.default_rng(0)

# 1. Second price: for every value v, highest other bid h and alternative bid b on a grid,
#    utility of bidding v is at least utility of bidding b. Ties are broken against us.
def u_second(v, b, h):
    return v - h if b > h else 0.0

grid = np.round(np.arange(0, 1.0001, 0.05), 2)
worse = sum(u_second(v, b, h) > u_second(v, v, h) + 1e-12 for v, b, h in product(grid, grid, grid))
print(f"second price: {len(grid)**3} (value, bid, rival) triples checked, "
      f"cases where a lie beats the truth: {worse}")

# 2. First price with n bidders, values uniform on [0, 1]. If rivals bid beta(x) = (n-1)/n x,
#    what should a bidder with value v bid? Expected utility = (v - b) * P(all rivals bid below b).
for n in (2, 5):
    v = 0.8
    bids = np.linspace(0, v, 801)
    p_win = np.clip(bids / ((n - 1) / n), 0, 1) ** (n - 1)
    eu = (v - bids) * p_win
    print(f"first price, n={n}, value {v}: best bid on a grid {bids[np.argmax(eu)]:.3f}, "
          f"theory (n-1)/n * v = {(n - 1) / n * v:.3f}")

# 3. Revenue equivalence: average revenue over many simulated auctions.
print("\nexpected revenue with n bidders, values uniform on [0, 1] (200000 auctions each)")
print("    n   second price   first price   theory (n-1)/(n+1)")
for n in (2, 3, 5, 10):
    vals = rng.random((200000, n))
    s = np.sort(vals, axis=1)
    second = s[:, -2].mean()                      # winner pays the second-highest value
    first = ((n - 1) / n * s[:, -1]).mean()       # winner pays her own shaded bid
    print(f"   {n:>2}      {second:.4f}       {first:.4f}        {(n - 1) / (n + 1):.4f}")

# 4. VCG for two items A and B. Bidder 1 wants both (worth 10 together, 0 for one);
#    bidder 2 wants A (worth 6); bidder 3 wants B (worth 6).
value = {1: lambda S: 10 if S == {"A", "B"} else 0,
         2: lambda S: 6 if "A" in S else 0,
         3: lambda S: 6 if "B" in S else 0}

def best_allocation(bidders):
    best, best_w = None, -1
    for owner in product([None] + bidders, repeat=2):       # owner of A, owner of B
        alloc = {i: {it for it, o in zip("AB", owner) if o == i} for i in bidders}
        w = sum(value[i](alloc[i]) for i in bidders)
        if w > best_w:
            best, best_w = alloc, w
    return best, best_w

everyone = [1, 2, 3]
alloc, welfare = best_allocation(everyone)
print("\nVCG: efficient allocation", {i: sorted(s) for i, s in alloc.items()}, "welfare", welfare)
revenue = 0
for i in everyone:
    _, w_without = best_allocation([j for j in everyone if j != i])
    others_now = sum(value[j](alloc[j]) for j in everyone if j != i)
    pay = w_without - others_now
    revenue += pay
    print(f"   bidder {i} pays {w_without} - {others_now} = {pay}, utility {value[i](alloc[i]) - pay}")
print("   seller's revenue", revenue, "(bidder 1 alone was willing to pay 10)")
