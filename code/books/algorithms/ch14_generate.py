"""Chapter 14: generating subsets, permutations and combinations by backtracking."""


def subsets(items):
    """Every subset: at depth i decide whether items[i] is in or out."""
    out, chosen = [], []

    def go(i):
        if i == len(items):
            out.append(list(chosen))
            return
        chosen.append(items[i])          # branch 1: take items[i]
        go(i + 1)
        chosen.pop()                     # undo, then branch 2: leave it
        go(i + 1)
    go(0)
    return out


def permutations(items):
    out, perm, used = [], [], [False] * len(items)

    def go():
        if len(perm) == len(items):
            out.append(list(perm))
            return
        for i, x in enumerate(items):
            if not used[i]:
                used[i] = True
                perm.append(x)
                go()
                perm.pop()               # undo the choice before trying the next
                used[i] = False
    go()
    return out


def combinations(n, k):
    """k-element subsets of 1..n in lexicographic order, pruning hopeless branches."""
    out, comb = [], []

    def go(start):
        if len(comb) == k:
            out.append(list(comb))
            return
        need = k - len(comb)
        for x in range(start, n - need + 2):   # leave room for the remaining picks
            comb.append(x)
            go(x + 1)
            comb.pop()
    go(1)
    return out


nodes = 0


def subset_sum(nums, target, prune):
    """All subsets of positive nums with the given sum; count the tree nodes visited."""
    global nodes
    nums = sorted(nums, reverse=True)
    suffix = [0] * (len(nums) + 1)
    for i in range(len(nums) - 1, -1, -1):
        suffix[i] = suffix[i + 1] + nums[i]
    found, chosen = [], []

    def go(i, total):
        global nodes
        nodes += 1
        if total == target:
            found.append(list(chosen))
            return
        if i == len(nums):
            return
        if prune and (total > target or total + suffix[i] < target):
            return                       # overshot, or even taking everything left is too little
        chosen.append(nums[i])
        go(i + 1, total + nums[i])
        chosen.pop()
        go(i + 1, total)
    go(0, 0)
    return found


if __name__ == "__main__":
    print("subsets of [a, b, c]:", subsets(["a", "b", "c"]))
    print("permutations of [1, 2, 3]:", permutations([1, 2, 3]))
    print("combinations C(5, 3):", combinations(5, 3))
    print("counts: 2^10 =", len(subsets(list(range(10)))), " 6! =", len(permutations(list(range(6)))),
          " C(20, 4) =", len(combinations(20, 4)))

    nums = [15, 22, 14, 26, 32, 9, 16, 8, 3, 11, 19, 27, 5, 7]
    for prune in (False, True):
        nodes = 0
        sols = subset_sum(nums, 53, prune)
        print(f"subset sum 53, pruning {prune!s:5}: {len(sols)} solutions, {nodes} nodes visited")
    print("one solution:", subset_sum(nums, 53, True)[0])
