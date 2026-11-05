# Big-O and running time

*How to compare algorithms without a stopwatch: count the steps as a function of the input size $n$, and keep
only the part that grows fastest.*

| Name | Big-O | Example on this site | $n = 10^6$ takes about |
|---|---|---|---|
| constant | $O(1)$ | reading `a[i]`, a [hash table](../data-structures/hash-table.md) lookup | 1 step |
| logarithmic | $O(\log n)$ | [binary search](../searching/binary-search.md) | 20 steps |
| linear | $O(n)$ | finding the largest value, [two pointers](../searching/two-pointers.md) | $10^6$ steps |
| linearithmic | $O(n \log n)$ | [merge sort](../sorting/merge-sort.md), [heapsort](../sorting/heapsort.md) | $2 \times 10^7$ steps |
| quadratic | $O(n^2)$ | [bubble sort](../sorting/bubble-sort.md), comparing all pairs | $10^{12}$ steps |
| exponential | $O(2^n)$ | trying every [subset](../backtracking/subsets-permutations.md) | hopeless |

## The idea

A stopwatch measures one program on one computer with one input. Change any of those and the time changes. What
stays the same is **how the work grows** when the input grows. If you double the input:

- an $O(n)$ algorithm does about twice the work,
- an $O(n^2)$ algorithm does about **four** times the work,
- an $O(\log n)$ algorithm does **one** more step,
- an $O(2^n)$ algorithm squares its work.

Big-O keeps exactly this and throws the rest away. $5n^2 + 3n + 20$ steps is written $O(n^2)$: for large $n$ the
$n^2$ term dominates, and the 5 depends on the computer anyway.

A modern computer does very roughly $10^8$ to $10^9$ simple steps per second. So for $n = 10^6$, an
$O(n \log n)$ sort finishes in well under a second, while an $O(n^2)$ sort needs $10^{12}$ steps: many minutes or
hours.

<figure class="play" data-play="growth"><span class="ai-tag">AI-created</span><figcaption><b>Try it.</b> Slide the number of items and watch the growth rates race, with the time at a billion simple steps a second (a round figure for one modern core).</figcaption></figure>

## How to find the Big-O of code

1. **A simple statement** (assignment, comparison, arithmetic, array access): $O(1)$.
2. **A loop:** (number of times it runs) × (cost of its body).
3. **Nested loops:** multiply. Two nested loops over $n$ values: $O(n^2)$.
4. **Statements one after another:** add, then keep the biggest. $O(n) + O(n^2) = O(n^2)$.
5. **A loop that halves (or doubles) its variable:** $O(\log n)$ times round.
6. **Recursion:** write a recurrence and solve it (see [Recursion](recursion.md)).

## Code

Three ways of looping over $n$ values, counting their steps. The output shows the gap opening up.

=== "Python"

    ```python
    --8<-- "foundations/growth.py"
    ```

=== "Java"

    ```java
    --8<-- "foundations/Growth.java"
    ```

=== "C++"

    ```cpp
    --8<-- "foundations/growth.cpp"
    ```

Output:

```
n halving linear pairs
10 3 10 45
100 6 100 4950
1000 9 1000 499500
4000 11 4000 7998000
```

Going from 1,000 to 4,000 values multiplies the linear work by 4, the pairs by 16, and adds only 2 halving steps.

## Worst, best and average case

The same algorithm can take different times on different inputs of the same size.
[Insertion sort](../sorting/insertion-sort.md) takes $n$ steps on a sorted list but about $n^2/2$ on a reversed
one. So we say which case we mean:

- **Worst case:** the most steps over all inputs of size $n$. This is a guarantee, and the usual meaning.
- **Average case:** the expected steps when every input is equally likely (or the algorithm flips coins, as in
  random-pivot [quicksort](../sorting/quicksort.md)).
- **Best case:** rarely useful on its own, but tells you when an algorithm is *adaptive*.
- **Amortized:** the average over a long sequence of operations, such as appending to a growing array (below).

## Common mistakes

- **Treating Big-O as exact time.** An $O(n)$ algorithm with a huge constant can lose to an $O(n \log n)$ one for
  every $n$ you will ever meet.
- **Forgetting hidden loops.** `x in list`, `list.remove`, string concatenation in a loop and `substring` copies
  are all $O(n)$ steps, not one.
- **Mixing up variables.** A graph algorithm is $O(V + E)$, not $O(n)$; a string search is $O(n + m)$.
- **Ignoring memory.** Space is measured the same way; an $O(n^2)$ table of a million rows does not fit.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: the Big-O of three small programs"

    | Code | Count | Big-O |
    |---|---|---|
    | `for i in range(n): for j in range(n): s += 1` | $n \cdot n$ | $O(n^2)$ |
    | `for i in range(n): for j in range(i): s += 1` | $0 + 1 + \cdots + (n-1) = \frac{n(n-1)}{2}$ | $O(n^2)$ |
    | `i = 1; while i < n: i *= 2` | $\lceil \log_2 n \rceil$ | $O(\log n)$ |
    | `for i in range(n): j = 1; while j < n: j *= 2` | $n \lceil \log_2 n \rceil$ | $O(n \log n)$ |
    | `for i in range(n): ...` then `for i in range(n): for j in range(n): ...` | $n + n^2$ | $O(n^2)$ |

??? abstract "The math: the exact definitions"

    For functions $f, g$ from positive integers to positive reals:

    $$
    f(n) = O(g(n)) \iff \exists\, c > 0,\ n_0 \text{ such that } f(n) \le c\,g(n) \text{ for all } n \ge n_0.
    $$

    $$
    f(n) = \Omega(g(n)) \iff \exists\, c > 0,\ n_0 \text{ such that } f(n) \ge c\,g(n) \text{ for all } n \ge n_0.
    $$

    $$
    f(n) = \Theta(g(n)) \iff f(n) = O(g(n)) \text{ and } f(n) = \Omega(g(n)).
    $$

    **Example.** $5n^2 + 3n + 20 = O(n^2)$: for $n \ge 1$, $5n^2 + 3n + 20 \le 5n^2 + 3n^2 + 20n^2 = 28n^2$, so
    $c = 28$, $n_0 = 1$ works.

    **Limits.** If $\lim_{n\to\infty} f(n)/g(n) = L$ with $0 < L < \infty$, then $f = \Theta(g)$. If the limit
    is 0, then $f = O(g)$ but not $\Omega(g)$ (written $f = o(g)$).

    **The usual order**, each one $o$ of the next, for any constants $0 < \varepsilon < 1 < c$:

    $$
    1 \;\prec\; \log n \;\prec\; n^{\varepsilon} \;\prec\; n \;\prec\; n \log n \;\prec\; n^2 \;\prec\; n^3 \;\prec\; c^n \;\prec\; n! \;\prec\; n^n.
    $$

    **The base of a logarithm does not matter** inside Big-O: $\log_a n = \frac{\log_b n}{\log_b a}$, a constant
    factor apart.

    **Useful sums:** $\sum_{i=1}^{n} i = \frac{n(n+1)}{2}$, $\;\sum_{i=0}^{k} 2^i = 2^{k+1} - 1$,
    $\;\sum_{i=1}^{n} \frac1i = \ln n + O(1)$, $\;\log_2 n! = n\log_2 n - n\log_2 e + O(\log n)$ (Stirling).

    **Amortized cost of a growing array.** When an array that doubles its capacity when full receives $n$
    appends, the copies cost at most $1 + 2 + 4 + \cdots + n < 2n$ in total, so each append costs $O(1)$ amortized,
    even though a single append can cost $O(n)$.

??? tip "Watch it step by step"

    Each column doubles $n$. Watch how the rows grow: the bottom two explode.

    <div class="cs-anim" data-anim="growth"></div>

??? info "Related ideas"

    - **P and NP.** Problems solvable in polynomial time ($O(n^k)$) form the class P. NP holds problems whose
      answers can be *checked* in polynomial time. Whether P = NP is the most famous open question in computer
      science; most believe not.
    - **Lower bounds** say no algorithm can do better, like the $\Omega(n \log n)$ bound for comparison
      [sorting](../sorting/index.md#the-n-log-n-limit).
    - **The RAM model** behind all this assumes every simple step costs the same. Real machines have caches, so
      walking memory in order is much faster than jumping around; that is why
      [quicksort](../sorting/quicksort.md) usually beats [heapsort](../sorting/heapsort.md).

## See also

- [Recursion](recursion.md): recurrences and the master theorem
- [Sorting](../sorting/index.md): the same problem at six different speeds

## References

- T. H. Cormen et al., *Introduction to Algorithms*, 4th ed., Chapter 3 (characterizing running times).
- D. E. Knuth, "Big Omicron and Big Omega and Big Theta", *SIGACT News* 8(2), 1976.
- R. Sedgewick, K. Wayne, *Algorithms*, 4th ed., §1.4 (analysis of algorithms).
