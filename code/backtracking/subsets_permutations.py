def subsets(items):
    """Every subset: for each item, first leave it out, then put it in."""
    out, chosen = [], []

    def go(i):
        if i == len(items):
            out.append(list(chosen))
            return
        go(i + 1)                            # without items[i]
        chosen.append(items[i])              # choose
        go(i + 1)                            # with items[i]
        chosen.pop()                         # un-choose (the "back" in backtracking)
    go(0)
    return out


def permutations(items):
    """Every ordering: fill the positions one by one with an item not used yet."""
    out, chosen, used = [], [], [False] * len(items)

    def go():
        if len(chosen) == len(items):
            out.append(list(chosen))
            return
        for i, x in enumerate(items):
            if not used[i]:
                used[i] = True; chosen.append(x)
                go()
                chosen.pop(); used[i] = False
    go()
    return out


def subset_sums(items, target):
    """Every subset (keeping the items' order) that adds up to target; all items positive.
    Prunes: stop as soon as the running sum is too big."""
    out, chosen = [], []

    def go(i, total):
        if total == target:
            out.append(list(chosen))
            return
        if i == len(items) or total > target:   # nothing left, or already too much: give up on this branch
            return
        chosen.append(items[i])
        go(i + 1, total + items[i])
        chosen.pop()
        go(i + 1, total)
    go(0, 0)
    return out


if __name__ == "__main__":
    print(subsets([1, 2, 3]))
    print(permutations([1, 2, 3]))
    print(subset_sums([3, 34, 4, 12, 5, 2], 9))
