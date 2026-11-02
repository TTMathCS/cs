# Fibonacci and the DP idea

*Each Fibonacci number is the sum of the two before it. Computing it straight from that rule takes exponential
time; remembering answers makes it linear. This is dynamic programming in its simplest form.*

| Naive recursion | With memory (DP) | Two variables | Fast doubling |
|---|---|---|---|
| $O(\varphi^n)$ calls | $O(n)$ time, $O(n)$ space | $O(n)$ time, $O(1)$ space | $O(\log n)$ multiplications |

## The idea

The Fibonacci numbers are $F(0) = 0$, $F(1) = 1$ and $F(n) = F(n-1) + F(n-2)$:
0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, ...

Turned directly into a recursive function, $F(5)$ calls $F(4)$ and $F(3)$; $F(4)$ calls $F(3)$ again and $F(2)$;
and so on. The same small values are worked out over and over: $F(20)$ makes **21,891** calls to find 6,765.

The fix is to **remember** each value the first time it is found. Then each $F(i)$ is computed once, and $F(n)$
needs only $n - 1$ additions. That is the whole idea of dynamic programming: *a recursion with overlapping
subproblems, plus a memory*.

## How it works

Three ways, from the slowest to the leanest:

1. **Naive:** `fib(n) = fib(n-1) + fib(n-2)`, no memory.
2. **Memoization (top-down):** the same function, but first look the answer up in a table; store it before
   returning. In Python, `@lru_cache` does this for you.
3. **Tabulation (bottom-up):** fill `f[0..n]` in a loop. Each step needs only the last two values, so two
   variables are enough.

## Code

=== "Python"

    ```python
    --8<-- "dp/fibonacci.py"
    ```

=== "Java"

    ```java
    --8<-- "dp/Fibonacci.java"
    ```

=== "C++"

    ```cpp
    --8<-- "dp/fibonacci.cpp"
    ```

Output: `6765 21891` (the naive version made 21,891 calls for $F(20)$), then `12586269025` three times for
$F(50)$, which the naive version would need about 40 billion calls to reach, then the first eleven values.

## When to use it

- **The pattern, not the numbers:** Fibonacci itself is rarely needed, but the same shape appears everywhere:
  counting ways to climb stairs taking 1 or 2 steps, tilings of a $2 \times n$ strip with dominoes, and many
  "how many ways" questions.
- **Whenever a recursion calls itself on the same arguments more than once**, add a memory.

## Common mistakes

- **Overflow:** $F(47)$ no longer fits in a 32-bit signed integer and $F(93)$ overflows 64 bits. The code uses
  64-bit `long`; Python's integers never overflow.
- **Memoizing with a mutable default argument** or a global that is never cleared between tests.
- **Recursion depth:** top-down memoization still recurses $n$ levels deep; for large $n$ use the loop.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: the call tree of F(5)"

    Without memory:

    ```text
    F(5)
    ├── F(4)
    │   ├── F(3)
    │   │   ├── F(2) ── F(1), F(0)
    │   │   └── F(1)
    │   └── F(2) ── F(1), F(0)
    └── F(3)
        ├── F(2) ── F(1), F(0)
        └── F(1)
    ```

    That is 15 calls; $F(3)$ is computed twice and $F(2)$ three times. With memory, the second $F(3)$ and the later
    $F(2)$s are looked up, and only 9 calls happen (one per value $F(0)..F(5)$, plus the look-ups).

    Bottom-up for $F(10)$:

    | $i$ | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
    |---|---|---|---|---|---|---|---|---|---|---|---|
    | $F(i)$ | 0 | 1 | 1 | 2 | 3 | 5 | 8 | 13 | 21 | 34 | 55 |

??? abstract "The math: how slow is the naive version, and a formula"

    **Counting calls.** Let $C(n)$ be the number of calls made by `fib_naive(n)`. Then $C(0) = C(1) = 1$ and
    $C(n) = 1 + C(n-1) + C(n-2)$. Adding 1 to both sides gives $C(n) + 1 = (C(n-1) + 1) + (C(n-2) + 1)$, the
    Fibonacci rule again, so

    $$C(n) = 2F(n+1) - 1.$$

    For $n = 20$: $2 \cdot 10946 - 1 = 21891$, exactly what the program counted.

    **Binet's formula.** With $\varphi = \frac{1 + \sqrt 5}{2} \approx 1.618$ (the golden ratio) and
    $\psi = \frac{1 - \sqrt 5}{2}$,

    $$F(n) = \frac{\varphi^n - \psi^n}{\sqrt 5}.$$

    Since $|\psi| < 1$, $F(n)$ is the whole number nearest to $\varphi^n / \sqrt 5$. So the naive recursion
    makes about $\frac{2\varphi}{\sqrt 5}\varphi^{n} \approx 1.45 \cdot 1.618^n$ calls: exponential.

    **Matrix form.**

    $$\begin{pmatrix} F(n+1) & F(n) \\ F(n) & F(n-1) \end{pmatrix} = \begin{pmatrix} 1 & 1 \\ 1 & 0 \end{pmatrix}^n$$

    With [fast exponentiation](../number-theory/fast-power.md) this needs only $O(\log n)$ matrix
    multiplications. The "fast doubling" identities $F(2k) = F(k)\,(2F(k+1) - F(k))$ and
    $F(2k+1) = F(k)^2 + F(k+1)^2$ do the same with less work.

??? tip "Watch it step by step"

    Orange cells are read, red is the cell being filled, green cells are finished.

    <div class="cs-anim" data-anim="fibonacci"></div>

??? info "Variations and related ideas"

    - **Climbing stairs:** the number of ways to climb $n$ steps taking 1 or 2 at a time is $F(n+1)$.
    - **Tribonacci** and other "sum of the last $k$" sequences: keep the last $k$ values.
    - **Fibonacci modulo $m$** repeats with a period (the Pisano period), at most $6m$.
    - **Fibonacci heaps** and **Fibonacci search** borrow the name because Fibonacci numbers appear in their analysis.

## See also

- [Recursion](../foundations/recursion.md)
- [Coin change](coin-change.md): the next step, a DP with a choice
- [Fast exponentiation](../number-theory/fast-power.md): $F(n)$ in $O(\log n)$

## References

- R. Bellman, *Dynamic Programming*, Princeton University Press, 1957.
- D. E. Knuth, *The Art of Computer Programming*, Vol. 1, 3rd ed., Section 1.2.8 (Fibonacci numbers).
- T. H. Cormen et al., *Introduction to Algorithms*, 4th ed., Chapter 14 (dynamic programming).
