# Radix sort

*Sort the numbers by their last digit, then by the digit before it, and so on, using a stable sort each time.
After the first digit's pass, the whole list is sorted.*

| Time | Extra space | Stable | Works on |
|---|---|---|---|
| $O(d\,(n + b))$ for $d$ digits in base $b$ | $O(n + b)$ | yes | whole numbers, fixed-length strings, dates |

## The idea

Card-sorting machines of the 1920s sorted punched cards by one column at a time, dealing them into 10 pockets.
The surprising trick is to start with the **least significant** digit (LSD). Sort everything by the ones digit,
then *stably* sort by the tens digit, then by the hundreds. Each pass keeps the order of the previous passes
whenever two numbers tie on the current digit, so after the last pass the numbers are ordered by hundreds, then
tens, then ones: completely sorted.

Each pass is a [counting sort](counting-sort.md) on one digit, which costs $O(n + b)$ with base $b$ (10 here).
For $d$ digits, the total is $O(d(n+b))$: linear in $n$ when the numbers have a fixed size.

## How it works

1. Find the largest value; it decides how many digits $d$ to process.
2. For `place` = 1, 10, 100, ... while `largest // place > 0`:
    - Stable counting sort the list by the digit `(x // place) % 10`.

## Code

=== "Python"

    ```python
    --8<-- "sorting/radix_sort.py"
    ```

=== "Java"

    ```java
    --8<-- "sorting/RadixSort.java"
    ```

=== "C++"

    ```cpp
    --8<-- "sorting/radix_sort.cpp"
    ```

Each program prints `[2, 24, 45, 66, 75, 90, 170, 802]`, `[329, 355, 436, 457, 657, 720, 839]` and `[0, 5, 5]`.

## When to use it

- **Many integers of fixed size**, such as 32-bit keys: with base $2^8$ that is 4 passes of a 256-counter
  counting sort, and it can beat $O(n \log n)$ sorts for large $n$.
- **Fixed-length strings** (postcodes, ID numbers, dates written as `YYYYMMDD`).
- **Suffix arrays** and other string algorithms are built from radix-sort passes.
- **Not** for floating-point numbers without a bit trick, or for variable-length keys without care.

## Common mistakes

- Using an unstable sort for a pass: the earlier passes' work is destroyed.
- Starting from the most significant digit with the LSD method: the answer is wrong. (MSD radix sort exists, but
  it sorts the buckets recursively, not the whole list.)
- Negative numbers: sort them separately, or flip the sign bit of two's-complement keys before sorting.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: [170, 45, 75, 90, 802, 24, 2, 66]"

    | Pass | Sorted by | Result |
    |---|---|---|
    | 1 | ones digit: 0, 5, 5, 0, 2, 4, 2, 6 | `170 90 802 2 24 45 75 66` |
    | 2 | tens digit: 7, 9, 0, 0, 2, 4, 7, 6 | `802 2 24 45 66 170 75 90` |
    | 3 | hundreds digit: 8, 0, 0, 0, 0, 1, 0, 0 | `2 24 45 66 75 90 170 802` |

    In pass 2, 170 and 75 both have tens digit 7; 170 stays ahead of 75 because it was ahead after pass 1. That
    is stability at work: in pass 3 both have the hundreds digits 1 and 0, which put them in the right order.

??? abstract "The math: correctness and choosing the base"

    **Correctness by induction.** Claim: after pass $j$, the list is sorted by the number formed by the last $j$
    digits. Pass $j+1$ sorts by digit $j+1$. Two numbers with different digit $j+1$ end up in the right order. Two
    with the same digit $j+1$ keep their order from pass $j$, which by the claim is the right order for their last
    $j$ digits. So the claim holds for $j+1$.

    **Time.** $d$ passes of counting sort: $T = \Theta(d(n+b))$. For $n$ keys of $w$ bits, using $r$ bits per pass
    (base $b = 2^r$) gives $d = \lceil w/r \rceil$ passes:

    $$
    T = \Theta\!\left(\frac{w}{r}\,(n + 2^r)\right).
    $$

    Choosing $r \approx \log_2 n$ (but not more than $w$) makes $2^r \approx n$ and
    $T = \Theta\!\left(\frac{w\,n}{\log_2 n}\right)$. For 32-bit keys and a million values, $r = 16$ gives just 2
    passes.

??? tip "Watch it step by step"

    Orange: reading one digit of every number. Blue: the list after the stable sort on that digit.

    <div class="cs-anim" data-anim="radix-sort"></div>

??? info "Variations and related ideas"

    - **MSD radix sort** starts with the most significant digit and recursively sorts each bucket. It can stop as
      soon as a bucket has one item, so it suits variable-length strings; this is how **American flag sort** and
      most fast string sorts work.
    - **Sorting floats:** flip all bits of negative IEEE-754 floats and only the sign bit of positive ones; the
      bit patterns then sort as unsigned integers.
    - **Suffix arrays:** the prefix-doubling method sorts suffixes by their first $2^k$ characters with two radix
      passes per round, $O(n \log n)$ in total.

## See also

- [Counting sort](counting-sort.md): the stable pass inside radix sort
- [Sorting overview](index.md)

## References

- H. Hollerith, US Patent 395,782 (1889), the tabulating machine; card sorters later sorted by one column per pass.
- T. H. Cormen et al., *Introduction to Algorithms*, 4th ed., §8.3.
- D. E. Knuth, *The Art of Computer Programming, Vol. 3*, 2nd ed., §5.2.5 (sorting by distribution).
