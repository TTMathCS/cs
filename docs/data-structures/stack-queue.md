# Stack and queue

*Two ways to line things up. A **stack** is a pile of plates: you take the one you put on last. A **queue** is a
line at a shop: the first to arrive is the first served.*

| | Add | Remove | Look at next | Order |
|---|---|---|---|---|
| Stack | push $O(1)$ | pop $O(1)$ | peek $O(1)$ | last in, first out (LIFO) |
| Queue | enqueue $O(1)$ | dequeue $O(1)$ | front $O(1)$ | first in, first out (FIFO) |

## The idea

**A stack** remembers what is still open. Reading `a[b(c)d]e` left to right, every opening bracket is pushed; every
closing bracket must match the bracket on top, which is the most recently opened one still unclosed. If the stack
is empty at the end, the text is balanced. Your computer runs every program on a stack, too: each function call
pushes a frame, and returning pops it (see [Recursion](../foundations/recursion.md)).

**A queue** keeps arrival order. It is the heart of [breadth-first search](../graphs/bfs.md), of printers, of web
servers handling requests, and of anything "first come, first served".

**How to build them so every operation is $O(1)$.** A stack is just a growing array, used only at its end. A
queue cannot simply remove from the front of an array (everything would shift), so it uses a **ring buffer**: an
array whose end wraps around to the start, with a `head` index for the front. When it fills up, copy into an array
twice as large.

## How it works (bracket check)

1. For each character: if it opens a bracket, push it.
2. If it closes one: the stack must not be empty, and the popped opener must be the matching kind.
3. At the end, the stack must be empty.

## Code

=== "Python"

    ```python
    --8<-- "data-structures/stack_queue.py"
    ```

=== "Java"

    ```java
    --8<-- "data-structures/StackQueue.java"
    ```

=== "C++"

    ```cpp
    --8<-- "data-structures/stack_queue.cpp"
    ```

Output: the five texts are balanced, not, not, balanced, balanced; then the queue gives `[1, 2, 3, 4, 5, 6, 7]`,
in arrival order, although it had to grow from 4 slots while wrapped around.

## When to use them

**Stack:** undo, the back button, matching brackets and tags, evaluating expressions (`3 4 + 2 *`), turning
recursion into a loop, [depth-first search](../graphs/dfs.md), and the "next greater element" family of problems
(a *monotonic stack*).

**Queue:** [breadth-first search](../graphs/bfs.md) and shortest paths in unweighted graphs, task scheduling,
buffers between a fast producer and a slow consumer, simulations. A **deque** (double-ended queue) allows both
ends and gives the sliding-window maximum.

## Common mistakes

- **Popping an empty stack** (check first, as `balanced` does).
- **Using a Python list as a queue** with `pop(0)`: each removal shifts every value, $O(n)$. Use
  `collections.deque`.
- **Using Java's old `Stack` class:** it is synchronized and slow; `ArrayDeque` is the modern choice.
- **Forgetting the wrap-around** (`% capacity`) in a ring buffer, or copying it in the wrong order when growing.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: \"a[b(c)d]e\""

    | Character | Action | Stack after (bottom → top) |
    |---|---|---|
    | a | not a bracket | (empty) |
    | [ | push | [ |
    | b | not a bracket | [ |
    | ( | push | [ ( |
    | c | not a bracket | [ ( |
    | ) | pop "(", it matches | [ |
    | d | not a bracket | [ |
    | ] | pop "[", it matches | (empty) |
    | e | not a bracket | (empty) |

    Empty at the end: balanced. For `([)]`, the `)` pops `[`: a mismatch, so not balanced.

??? abstract "The math: amortized O(1) for a growing array"

    One push that finds the array full must copy all $n$ items, which is $O(n)$. But that is rare. If the
    capacity doubles each time, then over $n$ pushes starting from capacity 1 the copies cost

    $$
    1 + 2 + 4 + \cdots + 2^{\lfloor \log_2 n \rfloor} < 2n,
    $$

    so all $n$ pushes cost less than $n + 2n = 3n$ steps: $O(1)$ **amortized** per push.

    **Potential method.** Define $\Phi = 2\cdot\text{size} - \text{capacity}$ (never negative after the first
    doubling). A normal push costs 1 and raises $\Phi$ by 2: amortized cost 3. A push that doubles from capacity
    $c$ (with size $c$) costs $c + 1$ and changes $\Phi$ from $c$ to $2(c+1) - 2c = 2$: amortized cost
    $c + 1 + 2 - c = 3$. Every push has amortized cost 3.

    Growing by a fixed amount (say 10 slots) instead of doubling makes the copies $10 + 20 + 30 + \cdots$, which
    is $\Theta(n^2)$ in total: always grow by a **factor**.

    **Balanced brackets and Catalan numbers.** The number of balanced strings of $n$ pairs of one bracket type is
    the Catalan number $C_n = \frac{1}{n+1}\binom{2n}{n}$: 1, 1, 2, 5, 14, 42, ...

??? tip "Watch it step by step"

    The stack is drawn left (bottom) to right (top). Then a queue: values join on the right and leave from the
    left.

    <div class="cs-anim" data-anim="stack-queue"></div>

??? info "Variations and related ideas"

    - **Monotonic stack:** keep the stack increasing; each value pops everything bigger than itself. Solves "next
      smaller element", "largest rectangle in a histogram" and the stock-span problem in $O(n)$.
    - **Two stacks make a queue:** push to an "in" stack; when the "out" stack is empty, pour "in" into it.
      $O(1)$ amortized per operation.
    - **Deque:** both ends. **Priority queue:** removes the smallest, not the oldest: see
      [binary heap](binary-heap.md).
    - **Shunting-yard** (Dijkstra, 1961) uses a stack to turn `3 + 4 * 2` into postfix `3 4 2 * +`.

## See also

- [Breadth-first search](../graphs/bfs.md) (queue) and [depth-first search](../graphs/dfs.md) (stack)
- [Binary heap](binary-heap.md): the priority queue
- [Big-O](../foundations/big-o.md): amortized cost

## References

- T. H. Cormen et al., *Introduction to Algorithms*, 4th ed., §10.1 (stacks and queues) and Chapter 16 (amortized analysis, dynamic tables).
- R. Sedgewick, K. Wayne, *Algorithms*, 4th ed., §1.3 (bags, queues and stacks).
