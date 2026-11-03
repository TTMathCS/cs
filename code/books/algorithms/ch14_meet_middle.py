"""Chapter 14: subset sum by meet in the middle, against plain enumeration."""
from bisect import bisect_left
import random


def all_sums(nums):
    """Sums of all 2^k subsets, built by doubling the list once per number."""
    sums = [0]
    for x in nums:
        sums = sums + [s + x for s in sums]
    return sums


def subset_sum_brute(nums, target):
    return target in set(all_sums(nums))


def subset_sum_mitm(nums, target):
    half = len(nums) // 2
    left = all_sums(nums[:half])
    right = sorted(all_sums(nums[half:]))
    for s in left:                         # need a right-half sum equal to target - s
        k = bisect_left(right, target - s)
        if k < len(right) and right[k] == target - s:
            return True
    return False


def closest_mitm(nums, target):
    """Largest subset sum not exceeding target (a knapsack with values = weights)."""
    half = len(nums) // 2
    left = all_sums(nums[:half])
    right = sorted(all_sums(nums[half:]))
    best = 0
    for s in left:
        if s > target:
            continue
        k = bisect_left(right, target - s + 1) - 1     # largest right sum <= target - s
        best = max(best, s + right[k])
    return best


if __name__ == "__main__":
    random.seed(1974)
    nums = [random.randint(10 ** 6, 10 ** 7) for _ in range(22)]
    target = sum(random.sample(nums, 9))
    print("22 numbers, target", target)
    print("enumerate all 2^22 sums:", subset_sum_brute(nums, target), " sums built:", 2 ** 22)
    print("meet in the middle:     ", subset_sum_mitm(nums, target), " sums built:", 2 * 2 ** 11)

    nums = [random.randint(10 ** 9, 10 ** 10) for _ in range(40)]
    cap = sum(nums) // 3
    best = closest_mitm(nums, cap)
    print(f"\n40 numbers, capacity {cap}: best subset sum {best}, gap {cap - best}")
    print(f"two lists of 2^20 = {2 ** 20} sums instead of 2^40 = {2 ** 40} subsets")
    small = nums[:16]
    c2 = sum(small) // 3
    brute = max(s for s in all_sums(small) if s <= c2)
    ok = closest_mitm(small, c2) == brute
    for _ in range(50):
        xs = [random.randint(1, 60) for _ in range(random.randint(1, 14))]
        t = random.randint(0, sum(xs) + 5)
        ok &= subset_sum_mitm(xs, t) == subset_sum_brute(xs, t)
    print("checks against full enumeration (closest sum, 50 random yes/no instances):", ok)
