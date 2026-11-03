# Chapter 24: the I/O model.  External merge sort on a simulated disk that
# counts block transfers, and how tall a B-tree is compared with a binary tree.
import heapq
import math
import random


class Disk:
    """Data lives in blocks of B records; every block read or write is one I/O."""
    def __init__(self, B):
        self.B, self.reads, self.writes = B, 0, 0

    def read_block(self, f, i):
        self.reads += 1
        return f[i * self.B:(i + 1) * self.B]

    def write_blocks(self, records):
        self.writes += math.ceil(len(records) / self.B)
        return list(records)


def external_merge_sort(data, M, B):
    disk = Disk(B)
    nblocks = math.ceil(len(data) / B)
    # Pass 0: read M records at a time, sort them in memory, write a run.
    runs, per_run = [], M // B
    for start in range(0, nblocks, per_run):
        chunk = []
        for i in range(start, min(start + per_run, nblocks)):
            chunk += disk.read_block(data, i)
        runs.append(disk.write_blocks(sorted(chunk)))
    passes = 0
    fan_in = M // B - 1                              # one block per run, one for output
    while len(runs) > 1:
        passes += 1
        new_runs = []
        for g in range(0, len(runs), fan_in):
            group = runs[g:g + fan_in]
            # Merge: each input run is read block by block (one block in memory each).
            for r in group:
                for i in range(math.ceil(len(r) / B)):
                    disk.read_block(r, i)
            merged = list(heapq.merge(*group))
            new_runs.append(disk.write_blocks(merged))
        runs = new_runs
    return runs[0], disk, passes


rng = random.Random(1988)
print("      N      M     B   runs  merge passes   I/Os   formula 2(N/B)(1 + passes)")
for N, M, B in [(10000, 1000, 100), (100000, 1000, 100), (100000, 10000, 100),
                (1000000, 10000, 1000)]:
    data = [rng.random() for _ in range(N)]
    out, disk, passes = external_merge_sort(data, M, B)
    assert out == sorted(data)
    ios = disk.reads + disk.writes
    runs = math.ceil(N / M)
    print(f"{N:8d} {M:6d} {B:5d} {runs:6d} {passes:8d}   {ios:9d}   {2 * (N // B) * (1 + passes):9d}")
print()

print("height needed to index N keys")
print("         N   binary tree   B-tree, B = 100   B-tree, B = 1000")
for N in (10**3, 10**6, 10**9, 10**12):
    print(f"  {N:.0e}   {math.ceil(math.log2(N + 1)):9d}   {math.ceil(math.log(N, 100) - 1e-9):14d}"
          f"   {math.ceil(math.log(N, 1000) - 1e-9):15d}")
