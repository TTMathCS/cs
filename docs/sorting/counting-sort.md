# Counting sort

*When the values are small whole numbers, don't compare them: count how many times each value appears, and use
the counts to write each value straight into its place.*

| Time | Extra space | Stable | Works on |
|---|---|---|---|
| $O(n + k)$ | $O(n + k)$ | yes | whole numbers from $0$ to $k$ (or keys that map to them) |

## The idea

Suppose 30 students got marks out of 10. Make 11 boxes labelled 0 to 10 and tally each mark in its box. Now read
the boxes in order: two 3s, five 4s, and so on. No mark was ever compared with another.

To sort **records** by a key (not just bare numbers), and to keep equal keys in their original order, one more
step is needed. Turn the tallies into **running totals**: after that, `count[v]` says how many keys are at most
$v$, which is exactly one past the last position where a key $v$ belongs. Then walk the input **from the back**,
placing each record at `count[key] - 1` and decreasing the count. Walking backwards is what makes it stable, and
stability is what lets [radix sort](radix-sort.md) build on it.

## How it works

1. `count = [0] * (k+1)`; for each value `x`, add 1 to `count[x]`.
2. For `v` from 1 to `k`: `count[v] += count[v-1]`.
3. For each value `x` from the **last** to the first: `count[x] -= 1`, then `out[count[x]] = x`.

## Code

=== "Python"

    ```python
    --8<-- "sorting/counting_sort.py"
    ```

=== "Java"

    ```java
    --8<-- "sorting/CountingSort.java"
    ```

=== "C++"

    ```cpp
    --8<-- "sorting/counting_sort.cpp"
    ```

Each program prints `[0, 0, 2, 2, 3, 3, 3, 5]`, `[1, 3, 3, 4, 4]` and `[0]`.

## When to use it

- **Keys in a small range:** ages, marks, letters, bytes, days of the year. When $k$ is about $n$ or smaller,
  it is linear time.
- **As one pass of [radix sort](radix-sort.md)**, which handles big numbers by sorting one digit at a time.
- **Not** when the range is huge compared with $n$: sorting 10 numbers below $10^9$ would need a billion
  counters.

## Common mistakes

- Placing from the front in step 3: the result is sorted but **not stable**.
- Forgetting negative values: shift every key by the minimum first (`x - min`), and back again.
- Off-by-one in the counter array: values $0..k$ need $k+1$ counters.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: [2, 5, 3, 0, 2, 3, 0, 3] with k = 5"

    | Value $v$ | 0 | 1 | 2 | 3 | 4 | 5 |
    |---|---|---|---|---|---|---|
    | tally | 2 | 0 | 2 | 3 | 0 | 1 |
    | running total (how many $\le v$) | 2 | 2 | 4 | 7 | 7 | 8 |

    Placing from the back: the last 3 goes to position $7-1=6$; the 0 before it to $2-1=1$; the next 3 to 5; the
    2 to 3; the 0 to 0; the 3 to 4; the 5 to 7; the first 2 to 2. Output: `[0, 0, 2, 2, 3, 3, 3, 5]`.

??? abstract "The math: why it is linear and why it is stable"

    **Time.** Step 1 is $n$ increments, step 2 is $k$ additions, step 3 is $n$ placements:
    $T(n,k) = \Theta(n + k)$. Space is the $k+1$ counters plus the $n$-slot output.

    **Correctness.** After step 2, $\text{count}[v] = |\{ i : a_i \le v \}|$. In sorted order the keys equal to $v$
    fill positions $\text{count}[v-1]$ to $\text{count}[v]-1$. Step 3 fills that block from its right end
    leftwards, one slot per key $v$, so every key lands inside its block.

    **Stability.** Within the block for $v$, the input is scanned from the back, so the last key $v$ in the input
    gets the rightmost slot, the one before it the next slot left, and so on: equal keys keep their input order.

    **Why it beats $n \log n$.** The $\Omega(n \log n)$ bound on the [sorting overview](index.md) only holds for
    algorithms that learn about the keys by comparing them. Counting sort uses a key as an array **index**, which
    gives it $\log_2(k+1)$ bits of information in one step instead of one bit per comparison.

??? tip "Watch it step by step"

    Row 1 is the input, row 2 the counters (indexed by value), row 3 the output (indexed by position).

    <div class="cs-anim" data-anim="counting-sort"></div>

??? info "Variations and related ideas"

    - **Bucket sort** spreads values that are spread evenly over $[0, 1)$ into $n$ buckets, sorts each small
      bucket with [insertion sort](insertion-sort.md), and joins them: $O(n)$ on average.
    - **Pigeonhole sort** is the simple tally-and-read version for bare numbers.
    - **Histogram and frequency counting** is step 1 on its own; prefix sums (step 2) are a tool of their own,
      for example the [Fenwick tree](../data-structures/fenwick-tree.md).

## See also

- [Radix sort](radix-sort.md): counting sort, one digit at a time
- [Sorting overview](index.md): the comparison lower bound

## References

- H. H. Seward, *Information Sorting in the Application of Electronic Digital Computers to Business Operations*, MIT M.S. thesis, 1954 (counting sort and radix sort).
- T. H. Cormen et al., *Introduction to Algorithms*, 4th ed., §8.2.
