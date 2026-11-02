# Coin change

*Find the fewest coins that make an amount, when each kind of coin can be used as often as you like. And,
with almost the same table, count how many different ways the amount can be made.*

| Time | Extra space | Coins | Output |
|---|---|---|---|
| $O(k \cdot A)$ for $k$ coin kinds and amount $A$ | $O(A)$ | any positive values | fewest coins (and which), or the number of ways |

## The idea

With US coins (1, 5, 10 and 25 cents), the obvious method works: take the largest coin that fits, repeat. But
that **greedy** rule fails for other coin sets. With coins 1, 3 and 4, the amount 6 is best made as 3 + 3 (two
coins), while greedy takes 4 + 1 + 1 (three).

Dynamic programming does not guess. Ask: *what was the last coin?* If the last coin was $c$, the rest is the best
way to make $x - c$. So

$$\text{best}[x] = 1 + \min_{c \le x} \text{best}[x - c], \qquad \text{best}[0] = 0.$$

Fill `best[1]`, `best[2]`, ..., `best[A]` in order; each needs only smaller amounts, already done.

Counting the ways is similar, with a twist: to count $\{1, 2\}$ and $\{2, 1\}$ as the **same** set, loop over the
coins on the outside. Then each set is built in one fixed order of coin kinds.

## How it works

**Fewest coins**

1. `best[0] = 0`; every other entry starts at infinity ("not possible yet").
2. For `x` from 1 to `A`, for each coin `c ≤ x`: if `best[x - c] + 1` is smaller, store it, and remember `c` in
   `last[x]`.
3. If `best[A]` is still infinity, the amount cannot be made. Otherwise follow `last[]` back from `A` to list the
   coins.

**Number of ways**

1. `ways[0] = 1` (the empty set of coins).
2. For each coin `c`, for `x` from `c` up to `A`: `ways[x] += ways[x - c]`.

## Code

=== "Python"

    ```python
    --8<-- "dp/coin_change.py"
    ```

=== "Java"

    ```java
    --8<-- "dp/CoinChange.java"
    ```

=== "C++"

    ```cpp
    --8<-- "dp/coin_change.cpp"
    ```

Output:

- `2 [3, 3]`: coins 1, 3 and 4 make 6 with two coins.
- `6 [1, 1, 1, 10, 25, 25]`: 63 cents in US coins.
- `-1 []`: 3 cannot be made from 2s.
- `4 242`: there are 4 ways to make 5 from 1, 2 and 5, and 242 ways to make a dollar from pennies, nickels,
  dimes and quarters.

## When to use it

- **Any "fewest pieces" problem with unlimited copies:** stamps, standard lengths of pipe, packaging sizes.
- **Checking whether a coin system is safe for greedy:** compare greedy with DP for all amounts up to the sum of
  the two largest coins (see "The math" below).
- **Counting combinations:** the number of ways to score a total in a game with fixed point values.

## Common mistakes

- **Using greedy** for coin sets where it is not safe.
- **Swapping the loops when counting:** with amounts on the outside, $1 + 2$ and $2 + 1$ are counted as two ways
  (that counts *orderings*, which is a different, also useful, question).
- **Adding 1 to infinity:** in Java and C++, `Integer.MAX_VALUE + 1` wraps around to a negative number; the code
  checks for "not possible" before adding.
- **Overflow when counting:** the number of ways grows very fast; use 64-bit integers or a modulus.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: coins 1, 3, 4 and the amount 6"

    | $x$ | try coin 1 | try coin 3 | try coin 4 | best[$x$] | last coin |
    |---|---|---|---|---|---|
    | 0 | | | | 0 | |
    | 1 | best[0] + 1 = 1 | | | 1 | 1 |
    | 2 | best[1] + 1 = 2 | | | 2 | 1 |
    | 3 | best[2] + 1 = 3 | best[0] + 1 = **1** | | 1 | 3 |
    | 4 | best[3] + 1 = 2 | best[1] + 1 = 2 | best[0] + 1 = **1** | 1 | 4 |
    | 5 | best[4] + 1 = **2** | best[2] + 1 = 3 | best[1] + 1 = 2 | 2 | 1 |
    | 6 | best[5] + 1 = 3 | best[3] + 1 = **2** | best[2] + 1 = 3 | 2 | 3 |

    Walk back from 6: last coin 3, leaving 3; last coin 3, leaving 0. Answer: 3 + 3.

    **Counting the ways to make 5 from 1, 2, 5:** after coin 1, `ways = [1, 1, 1, 1, 1, 1]`; after coin 2,
    `[1, 1, 2, 2, 3, 3]`; after coin 5, `[1, 1, 2, 2, 3, 4]`. The four ways: 5; 2+2+1; 2+1+1+1; 1+1+1+1+1.

??? abstract "The math: why the recurrence is right, and when greedy is safe"

    **Correctness.** Take any best way to make $x > 0$ and remove one coin $c$ from it. What is left makes
    $x - c$, and it must be a best way for $x - c$ (otherwise swapping in a better one would improve $x$). So
    $\text{best}[x] = 1 + \text{best}[x - c]$ for that $c$, and taking the minimum over all $c$ finds it.

    **Counting.** Let $W_j(x)$ be the number of ways to make $x$ with the first $j$ coin kinds. Either coin $j$ is
    not used, or it is used at least once:

    $$W_j(x) = W_{j-1}(x) + W_j(x - c_j).$$

    The inner loop going upwards over $x$ computes exactly this in one array.

    **Time.** $A$ amounts × $k$ coins = $O(kA)$. That is *pseudo-polynomial*: polynomial in the value $A$, but
    exponential in the number of digits used to write $A$. The general problem (with the amount written in binary)
    is NP-hard, so no known algorithm is polynomial in the number of digits.

    **When greedy is safe.** A coin system is called *canonical* when greedy is always optimal. Kozen and Zaks
    showed that if greedy fails at all, it already fails at some amount below $c_{k-1} + c_k$ (the two largest
    coins), so a DP over that range is a complete test. Pearson gave an $O(k^3)$ test.

??? tip "Watch it step by step"

    The red cell is being filled, the orange cell is `best[x - c]`. At the end the purple cells are the walk back.

    <div class="cs-anim" data-anim="coin-change"></div>

??? info "Variations and related ideas"

    - **Each coin at most once:** that is the [0/1 knapsack](knapsack.md) shape; loop amounts downwards.
    - **Ordered ways (compositions):** swap the loops; amounts outside, coins inside.
    - **Unbounded knapsack:** coins with values and weights, maximize value; the same loop as fewest coins.
    - **Frobenius number:** for two coins $a$ and $b$ with no common factor, the largest amount that cannot be
      made is $ab - a - b$.

## See also

- [0/1 knapsack](knapsack.md)
- [Fibonacci and the DP idea](fibonacci.md)
- [Greedy algorithms](../greedy/index.md): when the simple choice is enough

## References

- D. Kozen and S. Zaks, "Optimal bounds for the change-making problem", *Theoretical Computer Science* 123(2), 1994.
- D. Pearson, "A polynomial-time algorithm for the change-making problem", *Operations Research Letters* 33(3), 2005.
- T. H. Cormen et al., *Introduction to Algorithms*, 4th ed., Chapter 14 (dynamic programming).
