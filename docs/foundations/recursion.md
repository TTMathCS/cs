# Recursion

*A function that solves a problem by calling itself on a smaller version of the same problem, until the problem
is so small the answer is obvious.*

| Ingredients | Cost to watch | Typical tools |
|---|---|---|
| a base case and a smaller recursive case | call-stack depth and repeated work | recurrences, the master theorem, memoization |

## The idea

To move a tower of 3 discs in the Tower of Hanoi puzzle, you do not need to plan 7 moves. You only need to see
this: *if* you could move the top 2 discs out of the way, you would move the big disc, then move the 2 discs back
on top of it. Moving 2 discs is the same puzzle, smaller. And moving 0 discs is nothing at all.

That is recursion. Every recursive function has:

1. **A base case** that is answered directly (0 discs: do nothing; $0! = 1$).
2. **A recursive case** that reduces the problem to *smaller* versions of itself and combines their answers.

You **trust** the recursive call to work on the smaller problem, the same way a proof by induction trusts the
step before. If every call makes the problem smaller and the base case is right, the function is right.

Each call waits for the calls it makes, so the computer keeps a **call stack** of unfinished calls. Its depth is
the extra memory recursion uses; if it gets too deep (around a thousand frames in Python by default, more in Java
and C++), the program crashes with a stack overflow.

## How it works: the Tower of Hanoi

Move $n$ discs from peg A to peg C using peg B, one disc at a time, never a larger disc on a smaller one:

1. If $n = 0$, stop.
2. Move $n-1$ discs from A to B (using C).
3. Move disc $n$ from A to C.
4. Move $n-1$ discs from B to C (using A).

<figure class="play" data-play="fibtree"><span class="ai-tag">AI-created</span><figcaption><b>Watch the calls pile up.</b> A plain recursive Fibonacci, drawn call by call. The gold calls to fib(2) are the same work done again and again; remembering each answer (a memo) cuts the calls from exponential to about 2n.</figcaption></figure>

## Code

=== "Python"

    ```python
    --8<-- "foundations/hanoi.py"
    ```

=== "Java"

    ```java
    --8<-- "foundations/Hanoi.java"
    ```

=== "C++"

    ```cpp
    --8<-- "foundations/hanoi.cpp"
    ```

The programs print the 7 moves for 3 discs, then the move counts 1, 3, 7, 1023 and 1048575, and $10! = 3628800$.

## When to use it

- **The problem splits into smaller copies of itself:** trees, nested data, divide and conquer
  ([merge sort](../sorting/merge-sort.md), [quicksort](../sorting/quicksort.md)),
  [depth-first search](../graphs/dfs.md), [backtracking](../backtracking/index.md).
- **The recursive version is much clearer** than the loop version.
- **Prefer a loop** when the recursion is just a straight line (like factorial) and could be very deep, or in
  Python for depths beyond about a thousand.

## Common mistakes

- **No base case, or one that is never reached** (for example, the argument does not shrink): infinite
  recursion and a stack overflow.
- **Repeating work.** Naive recursive Fibonacci recomputes the same values exponentially often. Remembering
  answers (memoization) fixes it: see [dynamic programming](../dp/fibonacci.md).
- **Too deep for the stack:** recursion on a linked list or a path of $10^6$ nodes needs a loop or an explicit
  stack.
- **Modifying shared state** without undoing it, in backtracking.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: the calls of hanoi(3, A, C, B)"

    Indentation shows depth in the call stack.

    ```
    hanoi(3, A→C)
      hanoi(2, A→B)
        hanoi(1, A→C)      move disc 1 A→C
        move disc 2 A→B
        hanoi(1, C→B)      move disc 1 C→B
      move disc 3 A→C
      hanoi(2, B→C)
        hanoi(1, B→A)      move disc 1 B→A
        move disc 2 B→C
        hanoi(1, A→C)      move disc 1 A→C
    ```

    7 moves; the stack is at most 4 calls deep (3, 2, 1, and the empty call with 0 discs).

??? abstract "The math: recurrences and the master theorem"

    **Hanoi.** Let $T(n)$ be the number of moves. Then $T(0) = 0$ and $T(n) = 2T(n-1) + 1$. Adding 1 to both
    sides, $T(n) + 1 = 2\,(T(n-1) + 1)$, so $T(n) + 1 = 2^n$ and

    $$
    T(n) = 2^n - 1.
    $$

    No method can do better: the largest disc must move at least once, and before it does, the other $n-1$ discs
    must all be on the spare peg, which costs at least $T(n-1)$; afterwards they must come back, another
    $T(n-1)$. With 64 discs and one move per second this takes about 585 billion years.

    **Correctness by induction.** If `hanoi(n-1, ...)` is correct, then `hanoi(n, ...)` is: when disc $n$ moves,
    every smaller disc is on the spare peg, so source and target hold no smaller disc.

    **The master theorem** solves divide-and-conquer recurrences
    $T(n) = a\,T(n/b) + f(n)$ with $a \ge 1$, $b > 1$. Compare $f(n)$ with $n^{\log_b a}$:

    $$
    T(n) = \begin{cases}
    \Theta\!\left(n^{\log_b a}\right) & \text{if } f(n) = O\!\left(n^{\log_b a - \varepsilon}\right) \text{ for some } \varepsilon > 0,\\[4pt]
    \Theta\!\left(n^{\log_b a} \log n\right) & \text{if } f(n) = \Theta\!\left(n^{\log_b a}\right),\\[4pt]
    \Theta\!\left(f(n)\right) & \text{if } f(n) = \Omega\!\left(n^{\log_b a + \varepsilon}\right) \text{ and } a f(n/b) \le c f(n),\ c<1.
    \end{cases}
    $$

    | Recurrence | Example | Answer |
    |---|---|---|
    | $T(n) = T(n/2) + O(1)$ | [binary search](../searching/binary-search.md) | $\Theta(\log n)$ |
    | $T(n) = 2T(n/2) + O(n)$ | [merge sort](../sorting/merge-sort.md) | $\Theta(n \log n)$ |
    | $T(n) = 2T(n/2) + O(1)$ | sum of an array by halves | $\Theta(n)$ |
    | $T(n) = 3T(n/2) + O(n)$ | Karatsuba multiplication | $\Theta(n^{\log_2 3}) \approx \Theta(n^{1.585})$ |
    | $T(n) = T(n-1) + O(1)$ | factorial | $\Theta(n)$ (not a master-theorem case) |
    | $T(n) = 2T(n-1) + O(1)$ | Hanoi | $\Theta(2^n)$ |

??? tip "Watch it step by step"

    The three pegs as rows, discs listed from the bottom. Red is the disc that just moved.

    <div class="cs-anim" data-anim="hanoi"></div>

??? info "Related ideas"

    - **Tail recursion:** when the recursive call is the very last action, a compiler can turn it into a loop.
      C++ compilers often do; Python and Java do not.
    - **Recursion to iteration:** any recursion can be rewritten with an explicit stack, which is how deep
      [DFS](../graphs/dfs.md) is made safe.
    - **Memoization** turns exponential recursion into polynomial time when the same subproblems repeat: the
      starting point of [dynamic programming](../dp/index.md).
    - **Mutual recursion:** two functions that call each other, as in recursive-descent parsers.

## See also

- [Merge sort](../sorting/merge-sort.md) and [quicksort](../sorting/quicksort.md): divide and conquer
- [Fibonacci and the DP idea](../dp/fibonacci.md): when recursion repeats itself
- [Backtracking](../backtracking/index.md): recursion that explores choices

## References

- T. H. Cormen et al., *Introduction to Algorithms*, 4th ed., Chapter 4 (divide and conquer, the master theorem).
- R. L. Graham, D. E. Knuth, O. Patashnik, *Concrete Mathematics*, 2nd ed., §1.1 (the Tower of Hanoi).
- É. Lucas published the Tower of Hanoi puzzle in 1883 under the name "N. Claus de Siam".
