# 6. Games and adversarial search

*In every search so far, the world either did what we asked or picked outcomes without caring about us. In a game,
the other side picks its moves to beat us. This chapter answers the question: how should an agent choose a move when
an opponent is choosing against it? You will model games as search trees, compute the minimax value and prove that
it is the best you can guarantee, solve tic-tac-toe completely, prune the tree with alpha-beta and prove both that it
returns the right answer and how much it can save, see how chess programs cut the search off with evaluation functions,
build Monte Carlo tree search from scratch, add dice and hidden cards, and finally see how AlphaGo and AlphaZero joined
tree search to learned networks.*

!!! abstract "In this chapter"
    **You will learn:**

    - how a game becomes a search problem: players, moves, terminal tests, utilities, and the game tree
    - the minimax value, with a proof that it is optimal against an optimal opponent; tic-tac-toe solved in code
    - alpha-beta pruning, a full proof of correctness, and the best case $b^{\lceil d/2 \rceil} + b^{\lfloor d/2 \rfloor} - 1$ proved and measured
    - evaluation functions, depth cutoffs, quiescence search and the horizon effect, and what Deep Blue really did
    - Monte Carlo tree search with the UCT rule, from scratch
    - games of chance (expectiminimax) and games of imperfect information
    - how AlphaGo and AlphaZero combine tree search with policy and value networks

    **You need:** [Chapter 3](03-Uninformed-Search.md) (search trees, depth-first search) and
    [Chapter 4](04-Heuristic-Search.md) (heuristics). Expected value ([Probability](https://math.akadian.ca/books/probability/))
    for 6.5 and 6.6. Neural networks ([Machine learning, Chapter 15](../machine-learning/15-Neural-Networks-and-Backpropagation.md))
    help for 6.7 but are not required.

    **Levels:** 6.1 and 6.2 are beginner; 6.3 and 6.4 are intermediate (the proofs in 6.3 are advanced); 6.5 and 6.6
    are intermediate; 6.7 is advanced.

## 6.1 Games as search; zero-sum; game trees

You are X in tic-tac-toe. You could search for a sequence of moves that ends in three in a row, as in Chapter 3. But
half the moves in that sequence are not yours. Your opponent will not cooperate; a plan that needs O to play badly is
not a plan. We need a new kind of search.

The games in this chapter (until 6.6) are **deterministic, two-player, turn-taking, perfect-information, zero-sum**
games. Each word removes a complication:

- **deterministic:** no dice or shuffled cards;
- **two-player, turn-taking:** players called MAX and MIN alternate moves (MAX moves first);
- **perfect information:** both players see the whole state (unlike poker, with hidden cards);
- **zero-sum:** what one player wins, the other loses. In a game of win/lose/draw scored +1, 0, −1 for MAX, MIN's score
  is always the negative of MAX's, so one number per outcome describes both players' interests. (Chess with scores
  1, ½, 0 is **constant-sum**, which is the same thing up to a shift.)

Formally a game is given by:

- $S_0$, the initial state;
- $\text{To-Move}(s)$, the player whose turn it is in state $s$;
- $\text{Actions}(s)$, the legal moves, and $\text{Result}(s, a)$, the state after move $a$;
- $\text{Is-Terminal}(s)$, true when the game is over; such states are **terminal**;
- $\text{Utility}(s)$, the final score for MAX at a terminal state.

Together they define the **game tree**: the root is $S_0$, the children of a node are the results of its legal moves,
and the leaves are terminal states. A **ply** is one move by one player (chess players say a "move" is one ply by each
side, so we avoid that word). Tic-tac-toe's tree is small enough to search completely: the program in 6.2 visits all
549 946 of its nodes, with 255 168 leaves (finished games). Because the same position can be reached by different move
orders, these are only 5478 distinct positions; the tree is not the state space. Chess is another matter: with about 35
legal moves per position and games of 80 plies or so, the tree has roughly $35^{80} \approx 10^{123}$ nodes. Shannon,
in the 1950 paper that started computer chess, estimated $10^{120}$.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 310" role="img" aria-label="A two-ply game tree. The MAX root has three MIN children with leaves 4 9 6, 2 7 3 and 8 5 10. The MIN values are 4, 2 and 5, and the root value is 5, reached by the third move.">
<line x1="320" y1="55" x2="130" y2="125" stroke="currentColor" stroke-width="1.2"/>
<line x1="130" y1="158" x2="75" y2="237" stroke="currentColor" stroke-width="1.2"/>
<line x1="130" y1="158" x2="130" y2="237" stroke="currentColor" stroke-width="1.2"/>
<line x1="130" y1="158" x2="185" y2="237" stroke="currentColor" stroke-width="1.2"/>
<line x1="320" y1="55" x2="320" y2="125" stroke="currentColor" stroke-width="1.2"/>
<line x1="320" y1="158" x2="265" y2="237" stroke="currentColor" stroke-width="1.2"/>
<line x1="320" y1="158" x2="320" y2="237" stroke="currentColor" stroke-width="1.2"/>
<line x1="320" y1="158" x2="375" y2="237" stroke="currentColor" stroke-width="1.2"/>
<line x1="320" y1="55" x2="510" y2="125" stroke="currentColor" stroke-width="1.2"/>
<line x1="510" y1="158" x2="455" y2="237" stroke="currentColor" stroke-width="1.2"/>
<line x1="510" y1="158" x2="510" y2="237" stroke="currentColor" stroke-width="1.2"/>
<line x1="510" y1="158" x2="565" y2="237" stroke="currentColor" stroke-width="1.2"/>
<polygon points="320,22 302,54.4 338,54.4" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<polygon points="130,158 112,125.6 148,125.6" fill="#eea66f" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<rect x="60" y="237" width="30" height="26" rx="4" fill="none" stroke="currentColor" stroke-width="1.2"/><text x="75" y="255" font-size="13" text-anchor="middle" fill="currentColor">4</text>
<rect x="115" y="237" width="30" height="26" rx="4" fill="none" stroke="currentColor" stroke-width="1.2"/><text x="130" y="255" font-size="13" text-anchor="middle" fill="currentColor">9</text>
<rect x="170" y="237" width="30" height="26" rx="4" fill="none" stroke="currentColor" stroke-width="1.2"/><text x="185" y="255" font-size="13" text-anchor="middle" fill="currentColor">6</text>
<polygon points="320,158 302,125.6 338,125.6" fill="#eea66f" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<rect x="250" y="237" width="30" height="26" rx="4" fill="none" stroke="currentColor" stroke-width="1.2"/><text x="265" y="255" font-size="13" text-anchor="middle" fill="currentColor">2</text>
<rect x="305" y="237" width="30" height="26" rx="4" fill="none" stroke="currentColor" stroke-width="1.2"/><text x="320" y="255" font-size="13" text-anchor="middle" fill="currentColor">7</text>
<rect x="360" y="237" width="30" height="26" rx="4" fill="none" stroke="currentColor" stroke-width="1.2"/><text x="375" y="255" font-size="13" text-anchor="middle" fill="currentColor">3</text>
<polygon points="510,158 492,125.6 528,125.6" fill="#eea66f" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<rect x="440" y="237" width="30" height="26" rx="4" fill="none" stroke="currentColor" stroke-width="1.2"/><text x="455" y="255" font-size="13" text-anchor="middle" fill="currentColor">8</text>
<rect x="495" y="237" width="30" height="26" rx="4" fill="none" stroke="currentColor" stroke-width="1.2"/><text x="510" y="255" font-size="13" text-anchor="middle" fill="currentColor">5</text>
<rect x="550" y="237" width="30" height="26" rx="4" fill="none" stroke="currentColor" stroke-width="1.2"/><text x="565" y="255" font-size="13" text-anchor="middle" fill="currentColor">10</text>
<text x="350" y="45" font-size="15" text-anchor="start" fill="currentColor" font-weight="bold">5</text>
<text x="158" y="136" font-size="15" text-anchor="start" fill="currentColor" font-weight="bold">4</text>
<text x="348" y="136" font-size="15" text-anchor="start" fill="currentColor" font-weight="bold">2</text>
<text x="538" y="136" font-size="15" text-anchor="start" fill="currentColor" font-weight="bold">5</text>
<text x="211.0" y="88.0" font-size="12" text-anchor="middle" fill="currentColor" font-style="italic">a1</text>
<text x="332.0" y="88.0" font-size="12" text-anchor="middle" fill="currentColor" font-style="italic">a2</text>
<text x="429.0" y="88.0" font-size="12" text-anchor="middle" fill="currentColor" font-style="italic">a3</text>
<text x="30" y="45" font-size="13" text-anchor="start" fill="currentColor">MAX</text>
<text x="30" y="145" font-size="13" text-anchor="start" fill="currentColor">MIN</text>
<text x="30" y="255" font-size="13" text-anchor="start" fill="currentColor">leaf</text>
<text x="320" y="295" font-size="12" text-anchor="middle" fill="currentColor">utilities for MAX at the leaves; backed-up minimax values in bold</text>
</svg>
<figcaption>Figure 6.1. A two-ply game tree (one move by MAX, one reply by MIN). Each MIN node takes the smallest leaf below it (4, 2, 5); the MAX root takes the largest of those, 5, so MAX's minimax move is a3.</figcaption>
</figure>

## 6.2 Minimax, proved optimal against an optimal opponent

Look at Figure 6.1. MAX moves first, then MIN, then the game ends with the utility at the leaf. If MAX plays a1, MIN
will choose among 4, 9 and 6, and a MIN who wants MAX to score low picks 4. After a2, MIN picks 2; after a3, MIN picks
5. So a1 is worth 4 to MAX, a2 is worth 2 and a3 is worth 5. MAX should play a3. That is the whole idea: **back the
values up the tree, with MAX taking maxima and MIN taking minima.**

The **minimax value** of a state is defined by

$$
\text{Minimax}(s) =
\begin{cases}
\text{Utility}(s) & \text{if } s \text{ is terminal,}\\
\max_{a} \text{Minimax}(\text{Result}(s, a)) & \text{if MAX is to move,}\\
\min_{a} \text{Minimax}(\text{Result}(s, a)) & \text{if MIN is to move.}
\end{cases}
$$

The **minimax decision** at the root is the move that leads to the child of highest minimax value. The algorithm is
the definition: a depth-first recursion that computes the value of every child and takes the max or min.

### Why minimax is right

What does "the best move" mean when the opponent can do anything? A **strategy** for a player says which move to make
in every position where it is that player's turn. A game is finite if every path from the root ends at a terminal
state.

**Theorem.** In a finite two-player zero-sum game of perfect information, let $v = \text{Minimax}(S_0)$. Then

1. MAX has a strategy that guarantees a utility of at least $v$, whatever MIN does;
2. MIN has a strategy that holds MAX to at most $v$, whatever MAX does.

So $v$ is the **value of the game**: the most MAX can guarantee and the least MIN can concede. Playing the minimax move
is optimal against an optimal opponent.

*Proof*, by induction on the height of the tree (the longest path from the state to a terminal). For a terminal state
both claims hold with the empty strategy, since the utility is $v$. Suppose both claims hold for all states of smaller
height, and look at a state $s$ where MAX is to move. Every child $s'$ has smaller height, so by induction MAX has a
strategy $\sigma_{s'}$ guaranteeing at least $\text{Minimax}(s')$ from $s'$, and MIN has a strategy $\tau_{s'}$ holding
MAX to at most $\text{Minimax}(s')$.

- For claim 1, MAX plays the move $a^*$ to the child $s^*$ of largest value, which is $\text{Minimax}(s)$, and then
  follows $\sigma_{s^*}$. Whatever MIN does, MAX gets at least $\text{Minimax}(s^*) = \text{Minimax}(s)$.
- For claim 2, MIN waits to see MAX's move $a$, to some child $s'$, then follows $\tau_{s'}$. MAX gets at most
  $\text{Minimax}(s') \le \max_{a} \text{Minimax}(\text{Result}(s, a)) = \text{Minimax}(s)$.

A state where MIN is to move is the mirror image. $\square$

This is the finite case of a theorem that Ernst Zermelo proved for chess in 1913 (one of the two players can force a
win, or both can force a draw) and that John von Neumann generalised in his 1928 minimax theorem for games with
simultaneous moves ([Chapter 19](19-Multi-Agent-Systems.md)). Two cautions. First, minimax assumes the opponent plays
perfectly; against a weak opponent, another move may win more often, but no move does better against every
opponent. Second, the theorem says nothing about how to compute $v$ cheaply; for chess it is a statement about a tree
of $10^{120}$ nodes.

**Cost.** Minimax is a depth-first search of the whole tree. With branching factor $b$ and maximum depth $m$ it takes
$O(b^m)$ time and $O(bm)$ memory ($O(m)$ if moves are generated one at a time), exactly like depth-first search in
[Chapter 3](03-Uninformed-Search.md).

### Tic-tac-toe solved in code

The program solves tic-tac-toe three ways: plain minimax over the whole tree, alpha-beta (6.3), and minimax with a
**transposition table**, a dictionary that remembers the value of each position already solved so that a position
reached by different move orders is solved only once. That is memoisation, exactly as in
[the Algorithms book, Chapter 13](../algorithms/13-Dynamic-Programming.md).

```python
--8<-- "books/ai/ch06_tictactoe.py"
```

```
plain minimax    value +0   nodes visited  549946, 255168 finished games
alpha-beta       value +0   nodes visited   18297
minimax + table  value +0   nodes visited    5478
distinct positions reachable (incl. the empty board): 5478

value of each first move for X (rows of the board):
   +0  +0  +0
   +0  +0  +0
   +0  +0  +0

X in the top-left corner; value after each reply by O:
    X  +1  +1
   +1  +0  +1
   +1  +1  +1

perfect play, squares chosen: [0, 4, 1, 2, 6, 3, 5, 7, 8]  result 0
   X X O
   O O X
   X O X
```

What the output proves:

- The value of tic-tac-toe is 0: **with perfect play it is a draw.** Every first move by X is also a draw.
- After X takes a corner, every reply by O except the centre loses (value +1 for X). A beginner who answers a corner
  with an edge has already lost, and minimax knows it.
- Plain minimax visits all 549 946 nodes, alpha-beta 18 297, the transposition table 5478 (one per distinct position).
  On games with many transpositions the table is the bigger win; in real programs both are used together.

## 6.3 Alpha-beta pruning, correctness and best-case O(b^(d/2))

*Level: intermediate (the proofs are advanced).*

Look again at Figure 6.1, and search it from left to right. After a1, MAX knows it can get at least 4. Now it starts
on a2, and the first leaf below a2 is 2. MIN, at that node, can now hold MAX to 2 or less, whatever the other two leaves
are. MAX already has 4 elsewhere, so a2 will never be chosen, and **the other two leaves under a2 do not matter.** We
can skip them. The minimax value is the same; we just computed it without looking at everything.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 700 330" role="img" aria-label="The same tree searched by alpha-beta from left to right. Alpha-beta windows are written next to each node. After the first MIN node gives 4, the second MIN node sees the leaf 2, which is at most 4, so its other two leaves 7 and 3 are pruned. The third MIN node gives 5, and the root value is 5.">
<line x1="320" y1="55" x2="130" y2="125" stroke="currentColor" stroke-width="1.2"/>
<line x1="130" y1="158" x2="75" y2="237" stroke="currentColor" stroke-width="1.2"/>
<line x1="130" y1="158" x2="130" y2="237" stroke="currentColor" stroke-width="1.2"/>
<line x1="130" y1="158" x2="185" y2="237" stroke="currentColor" stroke-width="1.2"/>
<line x1="320" y1="55" x2="320" y2="125" stroke="currentColor" stroke-width="1.2"/>
<line x1="320" y1="158" x2="265" y2="237" stroke="currentColor" stroke-width="1.2"/>
<line x1="320" y1="158" x2="320" y2="237" stroke="currentColor" stroke-width="1.2" stroke-dasharray="4 3" stroke-opacity="0.6"/>
<line x1="320" y1="158" x2="375" y2="237" stroke="currentColor" stroke-width="1.2" stroke-dasharray="4 3" stroke-opacity="0.6"/>
<line x1="320" y1="55" x2="510" y2="125" stroke="currentColor" stroke-width="1.2"/>
<line x1="510" y1="158" x2="455" y2="237" stroke="currentColor" stroke-width="1.2"/>
<line x1="510" y1="158" x2="510" y2="237" stroke="currentColor" stroke-width="1.2"/>
<line x1="510" y1="158" x2="565" y2="237" stroke="currentColor" stroke-width="1.2"/>
<polygon points="320,22 302,54.4 338,54.4" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<polygon points="130,158 112,125.6 148,125.6" fill="#eea66f" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<rect x="60" y="237" width="30" height="26" rx="4" fill="none" stroke="currentColor" stroke-width="1.2"/><text x="75" y="255" font-size="13" text-anchor="middle" fill="currentColor">4</text>
<rect x="115" y="237" width="30" height="26" rx="4" fill="none" stroke="currentColor" stroke-width="1.2"/><text x="130" y="255" font-size="13" text-anchor="middle" fill="currentColor">9</text>
<rect x="170" y="237" width="30" height="26" rx="4" fill="none" stroke="currentColor" stroke-width="1.2"/><text x="185" y="255" font-size="13" text-anchor="middle" fill="currentColor">6</text>
<polygon points="320,158 302,125.6 338,125.6" fill="#eea66f" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<rect x="250" y="237" width="30" height="26" rx="4" fill="none" stroke="currentColor" stroke-width="1.2"/><text x="265" y="255" font-size="13" text-anchor="middle" fill="currentColor">2</text>
<rect x="305" y="237" width="30" height="26" rx="4" fill="none" stroke="currentColor" stroke-width="1.2" stroke-dasharray="4 3" stroke-opacity="0.6"/><text x="320" y="255" font-size="13" text-anchor="middle" fill="currentColor" fill-opacity="0.45">7</text>
<rect x="360" y="237" width="30" height="26" rx="4" fill="none" stroke="currentColor" stroke-width="1.2" stroke-dasharray="4 3" stroke-opacity="0.6"/><text x="375" y="255" font-size="13" text-anchor="middle" fill="currentColor" fill-opacity="0.45">3</text>
<polygon points="510,158 492,125.6 528,125.6" fill="#eea66f" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<rect x="440" y="237" width="30" height="26" rx="4" fill="none" stroke="currentColor" stroke-width="1.2"/><text x="455" y="255" font-size="13" text-anchor="middle" fill="currentColor">8</text>
<rect x="495" y="237" width="30" height="26" rx="4" fill="none" stroke="currentColor" stroke-width="1.2"/><text x="510" y="255" font-size="13" text-anchor="middle" fill="currentColor">5</text>
<rect x="550" y="237" width="30" height="26" rx="4" fill="none" stroke="currentColor" stroke-width="1.2"/><text x="565" y="255" font-size="13" text-anchor="middle" fill="currentColor">10</text>
<text x="350" y="45" font-size="13" text-anchor="start" fill="currentColor" font-weight="bold">5   [α=5]</text>
<text x="156" y="136" font-size="13" text-anchor="start" fill="currentColor" font-weight="bold">4  (α becomes 4)</text>
<text x="346" y="136" font-size="13" text-anchor="start" fill="currentColor" font-weight="bold">≤ 2: prune!</text>
<text x="536" y="136" font-size="13" text-anchor="start" fill="currentColor" font-weight="bold">5  (β: +∞ → 8 → 5)</text>
<text x="156" y="156" font-size="12" text-anchor="start" fill="currentColor">[α, β] = [−∞, +∞]</text>
<text x="346" y="156" font-size="12" text-anchor="start" fill="currentColor">[4, +∞]</text>
<text x="536" y="156" font-size="12" text-anchor="start" fill="currentColor">[4, +∞]</text>
<text x="375" y="282" font-size="12" text-anchor="middle" fill="currentColor" font-style="italic">pruned</text>
<text x="30" y="45" font-size="13" text-anchor="start" fill="currentColor">MAX</text>
<text x="30" y="145" font-size="13" text-anchor="start" fill="currentColor">MIN</text>
<text x="320" y="315" font-size="12" text-anchor="middle" fill="currentColor">7 of 9 leaves examined; the windows [α, β] are those passed down to each MIN node</text>
</svg>
<figcaption>Figure 6.2. Alpha-beta on the tree of Figure 6.1, children searched left to right. Once the second MIN node has found the leaf 2, its value can only be 2 or less, but MAX already has 4 from a1, so the leaves 7 and 3 cannot matter and are never looked at.</figcaption>
</figure>

### The algorithm

Alpha-beta carries two numbers down the tree:

- $\alpha$: the best value MAX is already guaranteed on the path to the current node (the highest so far);
- $\beta$: the best value MIN is already guaranteed on the path (the lowest so far).

A node's value matters to the root only if it lies strictly between $\alpha$ and $\beta$. As soon as a MIN node finds a
child of value $\le \alpha$, it stops: MAX above has something at least as good. As soon as a MAX node finds a child
of value $\ge \beta$, it stops: MIN above will not let play reach this node.

```python
def alphabeta(s, alpha, beta):
    if is_terminal(s):
        return utility(s)
    if to_move(s) == MAX:
        v = -inf
        for a in actions(s):
            v = max(v, alphabeta(result(s, a), alpha, beta))
            if v >= beta:
                return v            # beta cutoff
            alpha = max(alpha, v)
        return v
    else:
        v = +inf
        for a in actions(s):
            v = min(v, alphabeta(result(s, a), alpha, beta))
            if v <= alpha:
                return v            # alpha cutoff
            beta = min(beta, v)
        return v
```

The root call is `alphabeta(root, -inf, +inf)`.

### A trace by hand

On the tree of Figure 6.1, left to right:

| node | window passed in | leaves examined | value returned | why |
|---|---|---|---|---|
| MIN after a1 | $[-\infty, +\infty]$ | 4, 9, 6 | 4 | no cutoff possible; root sets $\alpha = 4$ |
| MIN after a2 | $[4, +\infty]$ | 2 | 2 | $2 \le \alpha = 4$: cut off, 7 and 3 skipped |
| MIN after a3 | $[4, +\infty]$ | 8, 5, 10 | 5 | $\beta$ falls to 8, then 5; no leaf $\le 4$ |
| root (MAX) | $[-\infty, +\infty]$ | | 5 | best of 4, 2, 5 |

Seven of nine leaves. If the moves had been ordered best first (a3, then a1, then a2), a3 would give 5 after three
leaves, and both a1 and a2 would be cut off after their first leaf (4 and 2, both $\le 5$): five leaves. That is the
best possible, $3^1 + 3^1 - 1 = 5$, as proved below.

### Correctness

The value returned for a2 was 2, and its true value is 2 as well, but alpha-beta did not know that: it knew only that
the value was at most 2. Had the skipped leaves been 7 and 0, the true value would be 0 and alpha-beta would still
return 2. Alpha-beta returns exact values only for nodes whose value lies inside the window, and **bounds** for the
others. Here is the precise statement
(due to Donald Knuth and Ronald Moore, 1975).

**Theorem.** Let $v$ be the minimax value of a node and $g$ the value returned by `alphabeta(node, α, β)` with
$\alpha < \beta$. Then

1. if $\alpha < g < \beta$, then $g = v$;
2. if $g \le \alpha$, then $v \le g$ (the true value is at most $g$, so at most $\alpha$);
3. if $g \ge \beta$, then $v \ge g$ (the true value is at least $g$, so at least $\beta$).

In particular, with the window $(-\infty, +\infty)$ case 1 always applies and the root's value is exact.

*Proof*, by induction on height. At a leaf, $g = v$ and all three statements hold. Take a MAX node with children
$c_1, \dots, c_k$ searched in order, with true values $v_i$ and returned values $g_i$. Child $i$ is searched with window
$(\alpha_i, \beta)$, where $\alpha_i = \max(\alpha, g_1, \dots, g_{i-1})$, and the node returns $g = \max(g_1, \dots, g_j)$,
where $j$ is the child at which the loop stopped (either $j = k$, or $g_j \ge \beta$ caused a cutoff).

*Case: a cutoff at child $j$.* Earlier children did not cut off, so $g_1, \dots, g_{j-1} < \beta$, and $g = g_j \ge \beta$.
By induction (statement 3 for child $j$), $v_j \ge g_j$. Then $v = \max_i v_i \ge v_j \ge g$: statement 3 holds.

*Case: no cutoff,* so $g = \max_i g_i < \beta$. For each child, either $g_i > \alpha_i$, and then $\alpha_i < g_i < \beta$
gives $v_i = g_i$ by induction, or $g_i \le \alpha_i$, and then $v_i \le g_i$ by induction. Either way $v_i \le g_i$, so
$v = \max_i v_i \le g$. That proves statement 2 if $g \le \alpha$. If instead $g > \alpha$, let $j$ be the first child with
$g_j = g$. Then $g_j$ is larger than all earlier $g_i$ and larger than $\alpha$, so $g_j > \alpha_j$, hence $v_j = g_j = g$ and
$v \ge g$. With $v \le g$ this gives $v = g$: statement 1.

A MIN node is the mirror image (swap max and min, $\alpha$ and $\beta$, and the inequalities). $\square$

### How much does it save? The best case, proved

The saving depends entirely on the **order** in which moves are tried. In the worst case alpha-beta examines every leaf
(it is easy to build trees where no cutoff ever happens). In the best case it examines far fewer.

**Theorem** (Knuth and Moore, 1975). In a uniform tree of branching factor $b$ and depth $d$, alpha-beta with perfect
move ordering (the best move always searched first) examines exactly

$$
b^{\lceil d/2 \rceil} + b^{\lfloor d/2 \rfloor} - 1
$$

leaves, and no algorithm that computes the minimax value can examine fewer, in the worst case over leaf values.

*Proof of the lower bound* (sketch). To be sure that the root's value is at least $v$, an algorithm must have seen a
MAX strategy that guarantees $v$: one move at each MAX node and every reply at each MIN node. That subtree has
$b^{\lfloor d/2 \rfloor}$ leaves (one choice at each of the $\lceil d/2 \rceil$ MAX levels, $b$ choices at each of the
$\lfloor d/2 \rfloor$ MIN levels). If any of its leaves were unseen, that leaf could be very low, and the guarantee would
fail. Likewise, to be sure the value is at most $v$, it must have seen a MIN strategy holding MAX to $v$, with
$b^{\lceil d/2 \rceil}$ leaves. The two subtrees share at least one leaf (the one reached when both strategies are
played), and they can share at most one, since they diverge as soon as either player has a choice. So at least
$b^{\lceil d/2 \rceil} + b^{\lfloor d/2 \rfloor} - 1$ leaves must be seen.

*Proof that perfect ordering achieves it.* With perfect ordering, the nodes alpha-beta visits fall into three types.
The root is a **PV node** (principal variation): its first child is a PV node, and its other children are **CUT nodes**,
which are refuted by their first child, so only that child is searched. The child of a CUT node is an **ALL node**, all
of whose children must be searched, and those children are CUT nodes again. Write $P(d)$, $C(d)$, $A(d)$ for the
number of leaves examined below a PV, CUT and ALL node of height $d$. Each is 1 at height 0, and

$$
P(d) = P(d-1) + (b-1)\,C(d-1), \qquad C(d) = A(d-1), \qquad A(d) = b\,C(d-1).
$$

So $C(d) = b\,C(d-2)$ with $C(0) = C(1) = 1$, which gives $C(d) = b^{\lfloor d/2 \rfloor}$, and then
$P(d) = 1 + (b-1)\sum_{k=0}^{d-1} b^{\lfloor k/2 \rfloor}$. The sum pairs up into geometric series; for example
$d = 3$ gives $1 + (b-1)(1 + 1 + b) = b^2 + b - 1$, and induction on $d$ gives $b^{\lceil d/2 \rceil} + b^{\lfloor d/2 \rfloor} - 1$
in general (Exercise 3). $\square$

In words: **perfect ordering roughly squares the number of positions you can afford**, or, equivalently, doubles the
depth you can search in the same time. The effective branching factor drops from $b$ to $\sqrt b$: about 6 instead of
35 for chess.

### Measured

The program builds uniform trees with random leaf values (stored in a NumPy array, with the value of every internal
node computed level by level), and counts the leaves alpha-beta examines under three orderings: worst child first,
the natural (random) order, and best child first, using the true values as an oracle.

```python
--8<-- "books/ai/ch06_alphabeta.py"
```

```
 b  d   all leaves   worst order  random order   best order   b^ceil(d/2)+b^floor(d/2)-1
 2 10         1024           853         276.8           63           63
 3  8         6561          5094        1290.0          161          161
 4  7        16384         12983        3045.0          319          319
 5  6        15625         13361        2572.0          249          249
 8  5        32768         29481        4120.8          575          575
10  4        10000          9520        1799.2          199          199

effective branching factor of random-order alpha-beta, measured on b=4, depth 4 to 8 (one tree each):
  depth 4:    120 leaves
  depth 5:    351 leaves   ratio to depth 4: 2.92
  depth 6:    969 leaves   ratio to depth 5: 2.76
  depth 7:   2357 leaves   ratio to depth 6: 2.43
  depth 8:   6982 leaves   ratio to depth 7: 2.96
  Pearl's asymptotic value for b=4: 2.630;  b^(3/4) = 2.828;  sqrt(b) = 2.000
```

- With the oracle ordering, the count equals $b^{\lceil d/2 \rceil} + b^{\lfloor d/2 \rfloor} - 1$ exactly, for every
  tree: the theorem, checked. For $b = 8$, $d = 5$ that is 575 leaves out of 32 768.
- Every run also asserts that alpha-beta returned the true minimax value.
- Worst-first ordering still prunes a little on these trees, but most leaves are examined.
- With random order the counts sit in between. Judea Pearl proved in 1982 that on such random trees alpha-beta's
  branching factor tends to $\xi_b / (1 - \xi_b)$, where $\xi_b$ is the positive root of $x^b + x - 1 = 0$; for $b = 4$ this is
  2.63, and the measured ratios (about 2.4 to 3.0, noisy at these small depths) are of that size. A common rule of thumb
  for random order is about $b^{3/4}$ per ply.

Real programs get close to the best case with cheap ordering tricks: try captures first; try the move that was best in
the last search (**iterative deepening**, which searches to depth 1, 2, 3, ... and uses each result to order the next);
try **killer moves** that caused cutoffs in sibling positions; and keep a **transposition table** of positions already
searched, usually indexed by a **Zobrist hash** (Albert Zobrist, 1970), a random 64-bit number per (piece, square)
XOR-ed together so that it updates in constant time per move.

<figure class="play" data-play="alphabeta"><span class="ai-tag">AI-created</span><figcaption><b>Watch it.</b> Alpha-beta on a small game tree with made-up leaf values: crossed-out leaves are never looked at, and the answer does not change.</figcaption></figure>

## 6.4 Evaluation functions, cutoffs, quiescence; Deep Blue (1997)

*Level: intermediate.*

Even with perfect ordering, chess to the end is out of reach: the full tree would still need about
$35^{40} \approx 10^{62}$ leaves. Shannon's 1950 answer is
still the basis of every classical game program: **search to a fixed depth, then estimate.**

Replace the terminal test by a **cutoff test** (for example, "depth $= d$") and the utility by an **evaluation function**
$\text{Eval}(s)$, a fast estimate of the minimax value from MAX's side:

$$
\text{H-Minimax}(s, \text{depth}) =
\begin{cases}
\text{Eval}(s) & \text{if Cutoff}(s, \text{depth}),\\
\max_a \text{H-Minimax}(\text{Result}(s, a), \text{depth} + 1) & \text{if MAX is to move,}\\
\min_a \text{H-Minimax}(\text{Result}(s, a), \text{depth} + 1) & \text{if MIN is to move.}
\end{cases}
$$

Alpha-beta applies unchanged. All the theorems of 6.2 and 6.3 now speak about the tree of depth $d$ with Eval at its
leaves: alpha-beta still computes exactly the H-Minimax value; whether that value is a good guide to the real game
depends on Eval.

### What makes a good evaluation function

- It must agree with the utility on terminal states (a checkmate is worse than any material advantage).
- It must be fast: it runs at every leaf of the search, and a slower Eval means a shallower search.
- For non-terminal states it should be strongly correlated with the chance of winning.

The classic form is a **weighted linear function** of **features**:

$$
\text{Eval}(s) = w_1 f_1(s) + w_2 f_2(s) + \dots + w_n f_n(s).
$$

In chess, beginners' books give the material values pawn 1, knight 3, bishop 3, rook 5, queen 9; then $f_1$ could be
(white pawns − black pawns) with $w_1 = 1$, and so on. Real programs add features for king safety, pawn structure,
mobility, control of the centre, with weights tuned by hand, by fitting to game results, or (since the 2010s) replaced
by a neural network. Linearity assumes features contribute independently, which is false (two bishops together are
worth more than twice one bishop), so programs add combination features. Learning the weights from data is
supervised learning ([Machine learning, Chapter 4](../machine-learning/04-Linear-Regression.md)); learning them from
self-play is reinforcement learning ([Chapter 15](15-Reinforcement-Learning.md)).

### Quiescence and the horizon effect

A fixed depth cutoff makes stupid mistakes. Suppose the search stops just after White captures a knight with its queen.
Eval counts material: White is a knight up. But on the next ply Black recaptures the queen. Positions where the
material is about to change are not **quiescent** (quiet), and Eval cannot be trusted on them.

**Quiescence search** extends the search at the cutoff, but only along "noisy" moves (captures, and sometimes checks
and promotions), until it reaches a quiet position, and evaluates there. At each node of the quiescence search the side
to move may also "stand pat" (decline to capture), so the extension can only help it. This is cheap, because the number
of captures is small, and it removes the worst errors.

A subtler failure is the **horizon effect**: facing an unavoidable loss (say, a trapped piece), the program makes
delaying moves (pointless checks, sacrificing pawns) that push the loss beyond its search depth, its horizon, so that
it no longer sees it. The search looks better and the position gets worse. Partial cures are **singular extensions**
(search deeper on a move that is clearly better than all its alternatives; Anantharaman, Campbell and Hsu, 1990, from
the Deep Thought team) and other selective extensions.

**Forward pruning** goes the other way: skip moves that look bad without searching them (beam search over moves, late
move reductions, **null-move pruning**, which gives the opponent a free move and prunes if the position is still too
good). These lose the guarantee of 6.3 but let the search go much deeper along the lines that matter.

### Deep Blue

IBM's Deep Blue defeated the world champion Garry Kasparov in a six-game match in New York in May 1997, by 3.5 to 2.5;
Kasparov had won their first match, in Philadelphia in 1996, by 4 to 2. The machine, described by its designers Murray
Campbell, A. Joseph Hoane and Feng-hsiung Hsu in 2002, was a 30-node IBM RS/6000 SP computer with 480 custom chess
chips, each a hardware move generator and evaluator. Its software ran a massively parallel alpha-beta search with
iterative deepening, transposition tables, quiescence search and extensive selective extensions, an evaluation
function computed mostly in hardware, an opening book and endgame databases. Its designers describe searching on the order of a hundred million positions per
second. Nothing in it was learned in the modern sense, and nothing in its search was conceptually beyond this chapter;
the achievement was engineering at an enormous scale. Since then, programs running on ordinary computers have become
far stronger than Deep Blue, and checkers was **solved** outright: Jonathan Schaeffer and colleagues proved in 2007, after
computations running since 1989, that checkers is a draw with perfect play.

## 6.5 Monte Carlo tree search and UCT

*Level: intermediate.*

Alpha-beta needs a good evaluation function. For Go, with its branching factor of about 250 and positions whose value
depends on subtle territory, nobody could write one, and alpha-beta programs played at a weak amateur level for
decades. The breakthrough was to evaluate a position **by playing it out at random**, many times, and to grow the
search tree towards the moves that look best.

**Monte Carlo tree search** (MCTS) keeps a tree of positions in memory. Each node stores $N$, the number of times it
has been visited, and $W$, the total reward of those visits for the player who made the move into it. Each
**iteration** has four phases (Figure 6.3):

1. **Selection.** From the root, repeatedly pick a child by a selection rule, until reaching a node that has an untried
   move (or is terminal).
2. **Expansion.** Add one child for an untried move.
3. **Simulation** (or **playout**, **rollout**). From the new node, play random moves until the game ends.
4. **Backpropagation.** Add 1 to $N$ of every node on the path, and add the result (1 for a win, ½ for a draw, 0 for a
   loss, from the point of view of the player who moved into that node) to $W$.

After the time runs out, play the move at the root with the **most visits** (more robust than the highest average).

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 250" role="img" aria-label="Four panels showing one iteration of Monte Carlo tree search: selection walks down the tree by the UCB rule, expansion adds one new node, simulation plays random moves to the end of the game, and backpropagation adds the result to every node on the path.">
<rect x="10" y="10" width="148" height="230" rx="8" fill="none" stroke="currentColor" stroke-width="1" stroke-opacity="0.5"/>
<text x="84" y="30" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">1. selection</text>
<line x1="84" y1="55" x2="50" y2="100" stroke="#eea66f" stroke-width="3"/>
<line x1="84" y1="55" x2="118" y2="100" stroke="currentColor" stroke-width="1.2"/>
<line x1="50" y1="100" x2="32" y2="145" stroke="currentColor" stroke-width="1.2"/>
<line x1="50" y1="100" x2="68" y2="145" stroke="#eea66f" stroke-width="3"/>
<circle cx="84" cy="55" r="11" style="fill:var(--md-default-bg-color)"/>
<circle cx="84" cy="55" r="11" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.2"/>
<circle cx="50" cy="100" r="11" style="fill:var(--md-default-bg-color)"/>
<circle cx="50" cy="100" r="11" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.2"/>
<circle cx="118" cy="100" r="11" style="fill:var(--md-default-bg-color)"/>
<circle cx="118" cy="100" r="11" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.2"/>
<circle cx="32" cy="145" r="11" style="fill:var(--md-default-bg-color)"/>
<circle cx="32" cy="145" r="11" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.2"/>
<circle cx="68" cy="145" r="11" style="fill:var(--md-default-bg-color)"/>
<circle cx="68" cy="145" r="11" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.2"/>
<text x="84" y="225" font-size="11" text-anchor="middle" fill="currentColor">pick max UCB child</text>
<rect x="168" y="10" width="148" height="230" rx="8" fill="none" stroke="currentColor" stroke-width="1" stroke-opacity="0.5"/>
<text x="242" y="30" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">2. expansion</text>
<line x1="242" y1="55" x2="208" y2="100" stroke="currentColor" stroke-width="1.2"/>
<line x1="242" y1="55" x2="276" y2="100" stroke="currentColor" stroke-width="1.2"/>
<line x1="208" y1="100" x2="190" y2="145" stroke="currentColor" stroke-width="1.2"/>
<line x1="208" y1="100" x2="226" y2="145" stroke="currentColor" stroke-width="1.2"/>
<line x1="226" y1="145" x2="226" y2="190" stroke="currentColor" stroke-width="1.2"/>
<circle cx="242" cy="55" r="11" style="fill:var(--md-default-bg-color)"/>
<circle cx="242" cy="55" r="11" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.2"/>
<circle cx="208" cy="100" r="11" style="fill:var(--md-default-bg-color)"/>
<circle cx="208" cy="100" r="11" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.2"/>
<circle cx="276" cy="100" r="11" style="fill:var(--md-default-bg-color)"/>
<circle cx="276" cy="100" r="11" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.2"/>
<circle cx="190" cy="145" r="11" style="fill:var(--md-default-bg-color)"/>
<circle cx="190" cy="145" r="11" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.2"/>
<circle cx="226" cy="145" r="11" style="fill:var(--md-default-bg-color)"/>
<circle cx="226" cy="145" r="11" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.2"/>
<circle cx="226" cy="190" r="11" style="fill:var(--md-default-bg-color)"/>
<circle cx="226" cy="190" r="11" fill="#7ccf9a" fill-opacity="0.8" stroke="currentColor" stroke-width="1.2"/>
<text x="268" y="194" font-size="11" text-anchor="start" fill="currentColor">new</text>
<rect x="326" y="10" width="148" height="230" rx="8" fill="none" stroke="currentColor" stroke-width="1" stroke-opacity="0.5"/>
<text x="400" y="30" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">3. simulation</text>
<line x1="400" y1="55" x2="366" y2="100" stroke="currentColor" stroke-width="1.2"/>
<line x1="400" y1="55" x2="434" y2="100" stroke="currentColor" stroke-width="1.2"/>
<line x1="366" y1="100" x2="348" y2="145" stroke="currentColor" stroke-width="1.2"/>
<line x1="366" y1="100" x2="384" y2="145" stroke="currentColor" stroke-width="1.2"/>
<line x1="384" y1="145" x2="384" y2="190" stroke="currentColor" stroke-width="1.2"/>
<circle cx="400" cy="55" r="11" style="fill:var(--md-default-bg-color)"/>
<circle cx="400" cy="55" r="11" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.2"/>
<circle cx="366" cy="100" r="11" style="fill:var(--md-default-bg-color)"/>
<circle cx="366" cy="100" r="11" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.2"/>
<circle cx="434" cy="100" r="11" style="fill:var(--md-default-bg-color)"/>
<circle cx="434" cy="100" r="11" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.2"/>
<circle cx="348" cy="145" r="11" style="fill:var(--md-default-bg-color)"/>
<circle cx="348" cy="145" r="11" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.2"/>
<circle cx="384" cy="145" r="11" style="fill:var(--md-default-bg-color)"/>
<circle cx="384" cy="145" r="11" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.2"/>
<circle cx="384" cy="190" r="11" style="fill:var(--md-default-bg-color)"/>
<circle cx="384" cy="190" r="11" fill="#7ccf9a" fill-opacity="0.8" stroke="currentColor" stroke-width="1.2"/>
<path d="M 384 201 l 8 8 l -10 6 l 9 7" fill="none" stroke="currentColor" stroke-width="1.2" stroke-dasharray="3 2"/>
<text x="426" y="220" font-size="11" text-anchor="middle" fill="currentColor">win / loss</text>
<rect x="484" y="10" width="148" height="230" rx="8" fill="none" stroke="currentColor" stroke-width="1" stroke-opacity="0.5"/>
<text x="558" y="30" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">4. backpropagation</text>
<line x1="558" y1="55" x2="524" y2="100" stroke="#eea66f" stroke-width="3"/>
<line x1="558" y1="55" x2="592" y2="100" stroke="currentColor" stroke-width="1.2"/>
<line x1="524" y1="100" x2="506" y2="145" stroke="currentColor" stroke-width="1.2"/>
<line x1="524" y1="100" x2="542" y2="145" stroke="#eea66f" stroke-width="3"/>
<line x1="542" y1="145" x2="542" y2="190" stroke="#eea66f" stroke-width="3"/>
<circle cx="558" cy="55" r="11" style="fill:var(--md-default-bg-color)"/>
<circle cx="558" cy="55" r="11" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.2"/>
<circle cx="524" cy="100" r="11" style="fill:var(--md-default-bg-color)"/>
<circle cx="524" cy="100" r="11" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.2"/>
<circle cx="592" cy="100" r="11" style="fill:var(--md-default-bg-color)"/>
<circle cx="592" cy="100" r="11" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.2"/>
<circle cx="506" cy="145" r="11" style="fill:var(--md-default-bg-color)"/>
<circle cx="506" cy="145" r="11" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.2"/>
<circle cx="542" cy="145" r="11" style="fill:var(--md-default-bg-color)"/>
<circle cx="542" cy="145" r="11" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.2"/>
<circle cx="542" cy="190" r="11" style="fill:var(--md-default-bg-color)"/>
<circle cx="542" cy="190" r="11" fill="#7ccf9a" fill-opacity="0.8" stroke="currentColor" stroke-width="1.2"/>
<text x="558" y="225" font-size="11" text-anchor="middle" fill="currentColor">N += 1, W += result</text>
</svg>
<figcaption>Figure 6.3. One iteration of Monte Carlo tree search. Selection follows the UCB1 rule down the part of the tree already stored; expansion adds one child (green); simulation plays random moves from it to the end of the game (dashed); backpropagation updates the visit count N and total reward W of every node on the path.</figcaption>
</figure>

### The selection rule: UCB1 and UCT

The selection rule must balance two needs: **exploitation** (look more at the moves that have done well) and
**exploration** (keep looking at moves that have been tried only a few times, because their averages are unreliable).
This is the **multi-armed bandit** problem ([Chapter 15](15-Reinforcement-Learning.md), 15.1): a gambler facing slot
machines with unknown payout rates must decide which arm to pull next. The **UCB1** rule (Peter Auer, Nicolò
Cesa-Bianchi and Paul Fischer, 2002) pulls the arm with the largest **upper confidence bound**

$$
\text{UCB1}(i) = \frac{W_i}{N_i} + c \sqrt{\frac{\ln N}{N_i}},
$$

where $N_i$ is the number of pulls of arm $i$, $W_i / N_i$ its average reward, $N$ the total number of pulls, and $c$ a
constant ($c = \sqrt 2$ in the original analysis, for rewards between 0 and 1). The first term is the estimate; the
second is a bonus that is large for arms tried rarely and shrinks as they are tried. Auer and colleagues proved that the
expected total loss compared with always pulling the best arm (the **regret**) grows only logarithmically in the number
of pulls, the best possible rate up to constants.

Levente Kocsis and Csaba Szepesvári's **UCT** (Upper Confidence bounds applied to Trees, 2006) uses UCB1 at every node
of the tree, treating the children as the arms. They proved that, for a finite game tree, the probability that UCT
chooses a wrong move at the root tends to zero as the number of iterations grows: with enough time it converges to the
minimax move. Rémi Coulom's program Crazy Stone, the same year, used a related scheme and introduced the name Monte
Carlo tree search.

A worked example of the rule: a node has been visited $N = 50$ times. Child A has $W = 6$ in $N_A = 10$ visits; child B
has $W = 2$ in $N_B = 2$. With $c = \sqrt 2$,

$$
\text{UCB}_A = 0.6 + 1.414\sqrt{\tfrac{\ln 50}{10}} \approx 0.6 + 0.885 = 1.485, \qquad
\text{UCB}_B = 1.0 + 1.414\sqrt{\tfrac{\ln 50}{2}} \approx 1.0 + 1.978 = 2.978,
$$

so B is selected: its average is high and, more importantly, based on only two visits.

### From scratch on tic-tac-toe

Tic-tac-toe is a good test because we know the right answers from 6.2.

```python
--8<-- "books/ai/ch06_mcts.py"
```

```
MCTS from the empty board, 3000 iterations: visits (and mean reward for X) per square
    245 (0.63)    139 (0.54)    343 (0.66)
    225 (0.61)    886 (0.75)    144 (0.55)
    471 (0.70)    177 (0.58)    370 (0.67)

after X takes square 0, O's most visited reply: square 4 with 1236 of 3000 visits (the only reply that does not lose is 4, the centre)

matches of 20 games (X moves first): wins for X / wins for O / draws
  UCT   10 iterations as X vs random : 16 /  3 /  1     as X vs perfect:  0 / 14 /  6     as O vs perfect: 15 /  0 /  5
  UCT  100 iterations as X vs random : 20 /  0 /  0     as X vs perfect:  0 /  0 / 20     as O vs perfect: 11 /  0 /  9
  UCT 1000 iterations as X vs random : 20 /  0 /  0     as X vs perfect:  0 /  0 / 20     as O vs perfect:  1 /  0 / 19
  UCT 4000 iterations as O vs perfect, 10 games: 0 / 0 / 10
```

What it shows:

- From the empty board, after 3000 iterations the centre has by far the most visits, then the corners, then the edges.
  All nine first moves are draws with perfect play, but against random continuations the centre wins most often, and
  MCTS's averages reflect the random playouts, not perfect play. With more iterations the tree grows deeper and the
  estimates move towards the minimax values.
- After X takes a corner, MCTS finds the only non-losing reply, the centre, as its most visited move.
- With 10 iterations per move, MCTS beats a random player but loses to a perfect one. With 100 it already draws every
  game as X against perfect play. As O (the harder side, since one slip loses), 100 iterations lose about half the games,
  1000 iterations lose one game in 20, and 4000 iterations drew all 10 games played. That is the behaviour the UCT
  theorem promises: more iterations, closer to minimax, with no evaluation function at all.

Why did MCTS take over Go and many other games? It needs only the rules (to generate moves and play out), not an
evaluation function; it is **anytime** (stop it whenever, and it has a best guess); it grows the tree **selectively**,
deep along promising lines and shallow elsewhere; and it parallelises well. Its weakness: random playouts can be very
misleading in positions where one precise line decides the game (a forced tactical sequence), which is exactly where
alpha-beta is strong. Chess programs therefore stayed with alpha-beta until learned evaluation arrived (6.7).

## 6.6 Chance: expectiminimax; imperfect information

*Level: intermediate.*

### Dice

In backgammon each player rolls two dice before moving, and the roll limits the legal moves. The game tree gets a third
kind of node: **chance nodes**, whose children are the possible outcomes, each with a probability. A chance node has no
player trying to maximise or minimise; its value is the **expected value** over outcomes:

$$
\text{Expectiminimax}(s) =
\begin{cases}
\text{Utility}(s) & \text{if } s \text{ is terminal,}\\
\max_a \text{Expectiminimax}(\text{Result}(s, a)) & \text{if MAX is to move,}\\
\min_a \text{Expectiminimax}(\text{Result}(s, a)) & \text{if MIN is to move,}\\
\sum_r P(r)\, \text{Expectiminimax}(\text{Result}(s, r)) & \text{if } s \text{ is a chance node.}
\end{cases}
$$

The same induction as in 6.2 proves that this is the best **expected** utility MAX can guarantee against an optimal
opponent. The cost grows: with $n$ distinct chance outcomes per chance node (21 for two dice, since order does not matter),
a depth-$m$ search costs $O(b^m n^m)$. Alpha-beta can be adapted (bounding the expectation needs bounds on the utility),
but it prunes much less. In practice, games with chance are searched only a few plies deep, and the evaluation function
carries most of the weight: Gerald Tesauro's TD-Gammon (described in a 1995 paper) learned its evaluation function by
self-play with temporal-difference learning ([Chapter 15](15-Reinforcement-Learning.md)) and played backgammon at the
level of strong human players with a search of only two or three plies.

**Evaluation functions under chance must be scaled correctly.** In minimax only the order of leaf values matters:
replacing every value by an increasing function of it (say its square, for positive values, or its rank) changes no
decision, because max and min only compare. Expectations add values, so that is no longer true.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 260" role="img" aria-label="An expectimax tree. MAX chooses A or B. Each leads to a chance node: with probability 0.9 the value is 2 for A or 1 for B, and with probability 0.1 the value is 3 for A or 40 for B. The expected values are 2.1 for A and 4.9 for B.">
<polygon points="320,22 302,54.4 338,54.4" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<line x1="320" y1="55" x2="180" y2="105" stroke="currentColor" stroke-width="1.2"/>
<text x="238.0" y="75" font-size="13" text-anchor="middle" fill="currentColor" font-style="italic">A</text>
<circle cx="180" cy="122" r="17" fill="#7ccf9a" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<text x="206" y="127" font-size="14" text-anchor="start" fill="currentColor" font-weight="bold">2.1</text>
<line x1="180" y1="139" x2="120" y2="197" stroke="currentColor" stroke-width="1.2"/>
<text x="134.0" y="168" font-size="12" text-anchor="middle" fill="currentColor">0.9</text>
<rect x="105" y="197" width="30" height="26" rx="4" fill="none" stroke="currentColor" stroke-width="1.2"/><text x="120" y="215" font-size="13" text-anchor="middle" fill="currentColor">2</text>
<line x1="180" y1="139" x2="240" y2="197" stroke="currentColor" stroke-width="1.2"/>
<text x="226.0" y="168" font-size="12" text-anchor="middle" fill="currentColor">0.1</text>
<rect x="225" y="197" width="30" height="26" rx="4" fill="none" stroke="currentColor" stroke-width="1.2"/><text x="240" y="215" font-size="13" text-anchor="middle" fill="currentColor">3</text>
<line x1="320" y1="55" x2="460" y2="105" stroke="currentColor" stroke-width="1.2"/>
<text x="402.0" y="75" font-size="13" text-anchor="middle" fill="currentColor" font-style="italic">B</text>
<circle cx="460" cy="122" r="17" fill="#7ccf9a" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<text x="486" y="127" font-size="14" text-anchor="start" fill="currentColor" font-weight="bold">4.9</text>
<line x1="460" y1="139" x2="400" y2="197" stroke="currentColor" stroke-width="1.2"/>
<text x="414.0" y="168" font-size="12" text-anchor="middle" fill="currentColor">0.9</text>
<rect x="385" y="197" width="30" height="26" rx="4" fill="none" stroke="currentColor" stroke-width="1.2"/><text x="400" y="215" font-size="13" text-anchor="middle" fill="currentColor">1</text>
<line x1="460" y1="139" x2="520" y2="197" stroke="currentColor" stroke-width="1.2"/>
<text x="506.0" y="168" font-size="12" text-anchor="middle" fill="currentColor">0.1</text>
<rect x="505" y="197" width="30" height="26" rx="4" fill="none" stroke="currentColor" stroke-width="1.2"/><text x="520" y="215" font-size="13" text-anchor="middle" fill="currentColor">40</text>
<text x="350" y="45" font-size="13" text-anchor="start" fill="currentColor" font-weight="bold">MAX picks B: 4.9 &gt; 2.1</text>
<text x="320" y="250" font-size="12" text-anchor="middle" fill="currentColor">circles: chance nodes (expected value); with values replaced by ranks 1-4 the choice flips to A</text>
</svg>
<figcaption>Figure 6.4. A tree with chance nodes. MAX's choice depends on the size of the leaf values, not only their order: B is better on average because of one rare large payoff. Replace the values by their ranks (1, 2, 3, 4) and A becomes better (2.1 against 1.3).</figcaption>
</figure>

The program below checks this on the tree of Figure 6.4, then solves a small dice game exactly. Two players race to 20
points. On your turn you choose to roll 1, 2 or 3 dice; if any die shows a 1, you score only 1 point, otherwise the sum.
More dice score more on average but risk the 1. The value of a position is the probability that the player to move
wins; MAX and MIN are folded into one function, since my winning probability is one minus my opponent's (this is the
**negamax** form of the recursion).

```python
--8<-- "books/ai/ch06_expectiminimax.py"
```

```
values as given          expected A =    2.10  B =    4.90  -> choose B
values squared           expected A =    4.50  B =  160.90  -> choose B
values replaced by rank  expected A =    2.10  B =    1.30  -> choose A

roll 1 dice: P(score only 1) = 0.167, expected points 3.500
roll 2 dice: P(score only 1) = 0.306, expected points 5.861
roll 3 dice: P(score only 1) = 0.421, expected points 7.366

first to 20: P(first player wins) with best play by both = 0.6232
best number of dice (rows: my score, columns: opponent's score; * = all equal)
        0  2  4  6  8 10 12 14 16 18
    0   3  3  3  3  3  3  3  3  3  3
    2   3  3  3  3  3  3  3  3  3  3
    4   3  3  3  3  3  3  3  3  3  3
    6   3  3  3  3  3  3  3  3  3  3
    8   3  3  3  3  3  3  3  3  3  3
   10   3  3  3  3  3  3  3  3  3  3
   12   2  2  2  3  3  3  3  3  3  3
   14   2  2  2  2  2  2  2  2  2  2
   16   1  1  2  2  2  2  2  2  2  2
   18   *  1  1  1  1  1  1  1  1  1
optimal player moving first vs 'always 1 dice': wins with probability 0.9593
optimal player moving first vs 'always 2 dice': wins with probability 0.7646
optimal player moving first vs 'always 3 dice': wins with probability 0.6366
```

- On the tiny tree, squaring the values keeps the decision (B), but replacing them by ranks, which preserves their order,
  flips it to A. In games of chance, Eval must be a positive linear transformation of the expected utility (for example
  the probability of winning), not just an order.
- In the dice game, the player who moves first wins 62 percent of the time with best play on both sides. Far behind or
  early, roll three dice (most points on average); near the target, roll fewer (protect the lead or take the sure
  points); at 18, needing 2, one die (which fails only on a 1) beats three (which fail unless all three avoid a 1,
  probability $(5/6)^3 \approx 0.58$). The `*` marks the one position where all choices are equally good: at 18 against an
  opponent at 0, who cannot reach 20 in one turn, any roll wins by the next turn.
- Playing the best response against simple fixed strategies wins 96, 76 and 64 percent of games against "always 1, 2,
  3 dice". "Always 3" is close to optimal; the decisions near the target are where the remaining edge lies.

### Imperfect information: cards you cannot see

In poker or bridge, each player sees only some of the cards. A player does not know the state; it knows a **belief
state**, a set of states (or a probability distribution over them) consistent with what it has seen, exactly as in
5.6. Worse, the opponent's actions reveal information about the opponent's cards, and good play must account for what
**its own** actions reveal: a player who always bets with good cards and never with bad ones is easy to read.

A tempting shortcut is to sample possible deals of the hidden cards, solve each as a perfect-information game, and
average. This **averaging over clairvoyance** is wrong in principle: it assumes that after the current move you will
know the cards, so it never values gathering information or hiding it. It still works reasonably in some card games
(it is used in bridge programs), but it cannot bluff.

The right solution concept is a **Nash equilibrium** of the game with hidden information ([Chapter 19](19-Multi-Agent-Systems.md)),
which usually requires **randomised** strategies: bluffing with a calculated probability. Even the tiny **Kuhn poker**
(three cards, one betting round, analysed by Harold Kuhn in 1950) needs mixed strategies. For large games the main
method is **counterfactual regret minimisation** (CFR; Zinkevich, Johanson, Bowling and Piccione, 2007), which plays
the game against itself many times, keeps for every decision the regret of not having played each action, and moves
towards actions with high regret; the average strategy converges to an equilibrium in two-player zero-sum games. With
it, Bowling and colleagues reported in 2015 that heads-up limit Texas hold'em is essentially solved, and Libratus
(Brown and Sandholm, reported in 2018) and DeepStack (Moravčík and colleagues, 2017) beat professional players at
heads-up no-limit hold'em.

## 6.7 AlphaGo and AlphaZero: how search and learning combine

*Level: advanced.*

By 2015 the best Go programs used MCTS and played at a strong amateur level, far from the best professionals. In
October 2015, AlphaGo beat the European champion Fan Hui 5 to 0, and in March 2016 it beat Lee Sedol, one of
the strongest players in the world, 4 to 1. The method, published by David Silver, Aja Huang and colleagues in *Nature*
in 2016, keeps MCTS and replaces its two weakest parts, the uniform choice of moves to explore and the random playouts,
by neural networks.

### AlphaGo (2016)

AlphaGo had three learned components (convolutional networks reading the 19 × 19 board as an image, see
[Machine learning, Chapter 17](../machine-learning/17-Convolutional-Networks.md)):

1. A **policy network** $p_\sigma(a \mid s)$, trained by supervised learning to predict the move a strong human would
   play, from about 30 million positions of games on the KGS Go server. The paper reports 57 percent accuracy at
   predicting the expert's move.
2. A second policy network $p_\rho$, initialised from the first and improved by **reinforcement learning**: playing
   games against earlier versions of itself and increasing the probability of moves in games it won (a policy gradient,
   [Chapter 15](15-Reinforcement-Learning.md)).
3. A **value network** $v_\theta(s)$, trained by regression to predict the winner of self-play games played by $p_\rho$
   from position $s$: an evaluation function, learned.

During play, MCTS selects moves inside the tree by a variant of UCB in which the policy network supplies a **prior**
$P(s, a)$, so that moves a strong player would consider are explored first:

$$
a^* = \arg\max_a \Big( Q(s, a) + c\, P(s, a) \frac{\sqrt{\sum_b N(s, b)}}{1 + N(s, a)} \Big).
$$

Here $Q(s, a)$ is the average value of the simulations through move $a$, and the bonus favours moves with high prior
and few visits. A new leaf was evaluated by mixing the value network's output with the result of a fast rollout,
using equal weights in the published version. The search therefore looks at a tiny fraction of the moves (those the
policy network likes) and judges positions with a learned evaluation instead of random play to the end.

### AlphaGo Zero and AlphaZero (2017, 2018)

AlphaGo Zero (Silver and colleagues, *Nature*, 2017) dropped the human games, the rollouts and the hand-made input
features. One network $f_\theta(s) = (\mathbf{p}, v)$ outputs both a move distribution and a value. Training is a loop:

1. Play games against itself, choosing each move by MCTS guided by $f_\theta$. At each position, the search produces
   **visit counts** over moves; normalised, they give a distribution $\boldsymbol{\pi}$ that is a stronger policy than
   $\mathbf{p}$ itself, because it has been improved by search.
2. Train the network so that $\mathbf{p}$ moves towards $\boldsymbol{\pi}$ and $v$ towards the actual game result
   $z \in \{-1, 0, +1\}$:

$$
\ell(\theta) = (z - v)^2 - \boldsymbol{\pi}^\top \log \mathbf{p} + \lambda \lVert\theta\rVert^2 .
$$

Then repeat with the improved network. This is **policy iteration** ([Chapter 14](14-Making-Decisions.md)) with search as the policy-improvement step and the
network as the memory of what the search found. Search makes the network's choices better; training makes the
network's choices more like the search; the next search starts from better guesses. The paper reports that AlphaGo
Zero, trained without any human games, defeated the version of AlphaGo that had beaten Lee Sedol by 100 games to 0.

AlphaZero (Silver and colleagues, *Science*, 2018) applied the same algorithm, with only the rules changed, to chess,
shogi and Go, and reported defeating strong existing programs in each: Stockfish in chess, Elmo in shogi and AlphaGo
Zero in Go. It searched far fewer positions per second than Stockfish, relying on the network to look only at
promising moves and to judge positions well. MuZero (Schrittwieser and colleagues, 2020) went further and learned a
model of the rules as well ([Chapter 15](15-Reinforcement-Learning.md), 15.6).

### What to take from it

The lesson is not "learning beats search" or the reverse. Every one of these systems is a tree search; the network
supplies the two things classical search needed humans for, **which moves to look at** (the policy, playing the role of
move ordering and forward pruning) and **how good a position is** (the value, playing the role of Eval). Search, in
turn, makes the network better than it could be alone. The same pairing, a fast learned intuition checked and improved
by explicit search, appears again in planning ([Chapter 10](10-Planning.md)) and in reasoning with learned models
([Chapter 21](21-Where-AI-Goes.md)).

### A short history thread

Zermelo's 1913 theorem on chess and von Neumann's 1928 minimax theorem gave the mathematics. Shannon's 1950 paper
"Programming a computer for playing chess" set out search to a fixed depth with an evaluation function and the idea of
selective search; Alan Turing wrote a chess program in the same years and, with no computer able to run it, executed it
by hand. Arthur Samuel's checkers program (described in 1959) learned its evaluation function by playing against
itself, decades before TD-Gammon and AlphaZero. Alpha-beta was found independently by several people in the late
1950s and early 1960s; Knuth and Moore's 1975 paper gave its definitive analysis. Deep Blue (1997) was the peak of
alpha-beta with hand-made evaluation; checkers was solved in 2007; MCTS (2006) transformed Go; AlphaGo (2016) and
AlphaZero (2018) joined search to deep learning; and CFR-based programs reached professional strength in two-player
poker by 2017.

## Check yourself

??? question "1. Compute the minimax value of a two-ply tree whose MIN nodes have leaves (3, 1, 8), (7, 6, 5) and (2, 9, 4). Then run alpha-beta left to right: which leaves are skipped?"

    The MIN values are 1, 5 and 2, so the root (MAX) value is 5 and MAX plays the middle move. Alpha-beta: the first
    MIN node examines 3, 1, 8 and returns 1 ($\alpha = 1$). The second examines 7, 6, 5: no leaf is $\le 1$, so nothing is
    pruned; it returns 5 ($\alpha = 5$). The third examines 2, which is $\le 5$: cut off, skipping 9 and 4. Seven leaves
    examined. With best ordering (middle move first) only $3 + 1 + 1 = 5$ would be needed.

??? question "2. How many leaves does alpha-beta examine with perfect ordering on a uniform tree with b = 3, d = 4? With b = 35 and d = 10, compare with minimax."

    $3^2 + 3^2 - 1 = 17$ of $3^4 = 81$. For $b = 35$, $d = 10$: minimax examines $35^{10} \approx 2.76 \times 10^{15}$
    leaves, perfect alpha-beta $2 \cdot 35^5 - 1 = 105\,043\,749 \approx 1.05 \times 10^8$, about 26 million times fewer.
    In other words, the depth reachable in a fixed time roughly doubles.

??? question "3. Prove by induction that P(d) = 1 + (b − 1)(b^⌊0/2⌋ + b^⌊1/2⌋ + ... + b^⌊(d−1)/2⌋) equals b^⌈d/2⌉ + b^⌊d/2⌋ − 1."

    Let $F(d) = b^{\lceil d/2 \rceil} + b^{\lfloor d/2 \rfloor} - 1$. At $d = 0$, $P(0) = 1 = 1 + 1 - 1$. Suppose $P(d) = F(d)$.
    Then $P(d+1) = P(d) + (b-1) b^{\lfloor d/2 \rfloor}$. If $d = 2k$: $F(d) = 2b^k - 1$ and
    $P(d+1) = 2b^k - 1 + b^{k+1} - b^k = b^{k+1} + b^k - 1 = F(2k+1)$. If $d = 2k+1$: $F(d) = b^{k+1} + b^k - 1$ and
    $P(d+1) = b^{k+1} + b^k - 1 + b^{k+1} - b^k = 2b^{k+1} - 1 = F(2k+2)$. $\square$

??? question "4. Why does a transposition table not change the minimax value, and why must it be used carefully together with alpha-beta?"

    The minimax value of a position depends only on the position (and whose turn it is), not on how it was reached, so
    storing it and reusing it gives the same value. With alpha-beta, however, a value returned with a window $(\alpha, \beta)$
    may be only a bound (6.3, statements 2 and 3). A table must therefore store, with each value, whether it is
    exact, a lower bound or an upper bound, and use it only when that is enough for the current window. Storing a bound
    as if it were exact is a classic bug.

??? question "5. Write code: a negamax version of alpha-beta for tic-tac-toe, and count nodes with the move order 0 to 8 and with centre, corners, edges first."

    Negamax uses $\max(a, b) = -\min(-a, -b)$: the value for the player to move is the maximum of the negated values
    of the children, and the window $(\alpha, \beta)$ becomes $(-\beta, -\alpha)$ one level down.

    ```python
    LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
    ORDER = [4, 0, 2, 6, 8, 1, 3, 5, 7]            # centre, corners, edges
    nodes = 0

    def negamax(b, player, alpha, beta, order):
        """Value for the player to move: +1 win, 0 draw, -1 loss."""
        global nodes
        nodes += 1
        other = "O" if player == "X" else "X"
        if any(b[i] == b[j] == b[k] == other for i, j, k in LINES):
            return -1                            # the previous move won
        if "." not in b:
            return 0
        best = -2
        for i in order:
            if b[i] == ".":
                v = -negamax(b[:i] + player + b[i + 1:], other, -beta, -alpha, order)
                best = max(best, v)
                alpha = max(alpha, v)
                if alpha >= beta:
                    break
        return best

    for name, order in (("0..8", list(range(9))), ("centre, corners, edges", ORDER)):
        nodes = 0
        v = negamax("." * 9, "X", -2, 2, order)
        print(f"{name:24s} value {v:+d}  nodes {nodes}")
    ```

    Output: `0..8` gives value +0 with 18297 nodes (the same count as the two-function version in 6.2);
    `centre, corners, edges` gives +0 with 7275 nodes. A simple ordering rule cuts the search by 60 percent.

??? question "6. Write code: solve Nim with three heaps by minimax (a move removes any positive number of objects from one heap; whoever takes the last object wins), and check the rule that the player to move wins exactly when the XOR of the heap sizes is not 0."

    ```python
    from functools import lru_cache

    @lru_cache(maxsize=None)
    def wins(heaps):
        """True if the player to move wins (normal play: whoever takes the last object wins)."""
        for i, h in enumerate(heaps):
            for take in range(1, h + 1):
                nxt = tuple(sorted(heaps[:i] + (h - take,) + heaps[i + 1:]))
                if not wins(nxt):
                    return True                 # a move to a losing position for the opponent
        return False

    bad = 0
    for a in range(8):
        for b in range(a, 8):
            for c in range(b, 8):
                if wins((a, b, c)) != ((a ^ b ^ c) != 0):
                    bad += 1
    print("positions up to (7,7,7) where minimax disagrees with the XOR rule:", bad)
    print("(3, 4, 5): first player wins?", wins((3, 4, 5)), " 3 xor 4 xor 5 =", 3 ^ 4 ^ 5)
    ```

    It prints 0 disagreements, and `True` with XOR 2 for (3, 4, 5). This is minimax with utilities ±1 written as
    "win/lose", plus a transposition table (sorting the heaps merges positions that differ only in order). Charles
    Bouton proved the XOR rule in 1901.

??? question "7. In MCTS, a node has N = 50 visits; child A has W = 6, N = 10; child B has W = 2, N = 2. Which does UCB1 with c = √2 select? Which would it select with c = 0.5?"

    With $c = \sqrt 2$: A scores $0.6 + 1.414 \cdot 0.6255 \approx 1.485$, B scores $1.0 + 1.414 \cdot 1.3986 \approx 2.978$, so B.
    With $c = 0.5$: A scores $0.6 + 0.5 \cdot 0.6255 \approx 0.913$, B scores $1.0 + 0.5 \cdot 1.3986 \approx 1.699$: still B,
    since its average is also higher. B would lose only if its average were much lower: for example with $W = 0$, $N = 2$
    and $c = 0.5$, B scores $0.699 < 0.913$ and A is selected.

??? question "8. Explain the horizon effect with an example, and why quiescence search does not fully cure it."

    A program searching 6 plies sees that its bishop is trapped and will be captured in 5 plies. It finds a pawn
    sacrifice that forces a recapture and delays the bishop's capture to ply 7, beyond its horizon; the evaluation at
    ply 6 now shows only the lost pawn, so it prefers the sacrifice, and loses the pawn and later the bishop. Quiescence
    search extends only noisy moves (captures) at the leaves; the bishop's capture is pushed beyond the horizon by quiet
    intermediate moves, which quiescence does not follow. Extensions for forcing moves and deeper search reduce the
    problem but no fixed rule removes it.

??? question "9. Prove that in a game without chance nodes, replacing every leaf value u by f(u), where f is strictly increasing, does not change the minimax decision. Why does the proof fail with chance nodes?"

    By induction on height, the new minimax value of every node is $f$ of the old one: at a leaf by definition; at a MAX
    node, $\max_i f(v_i) = f(\max_i v_i)$ because $f$ is increasing, and the maximising child is the same; likewise for
    min. So every choice is the same. At a chance node we would need $\sum_r P(r) f(v_r) = f(\sum_r P(r) v_r)$, which
    holds for all distributions only when $f$ is affine, $f(u) = au + c$ with $a > 0$. Figure 6.4 shows an increasing $f$
    (the rank) that changes the decision.

??? question "10. In the dice game, at 18 points against an opponent at 10, why is one die better than three? Compute the probability of winning on this turn for each choice."

    You need 2 points. With one die you fail only on a 1: success $5/6 \approx 0.833$. With three dice you score at
    least 3 if none shows a 1, which has probability $(5/6)^3 \approx 0.579$; otherwise you score 1. With two dice,
    $(5/6)^2 \approx 0.694$. The expected number of points is irrelevant here: only reaching 2 matters, and one die is
    safest. (If you fail, you are at 19 and need any roll next turn, but the opponent gets a turn first.)

??? question "11. Why does averaging over clairvoyance never bluff? Use a one-card example."

    In averaging over clairvoyance, each sampled deal is solved as if both players saw all cards. In every such game, a
    player holding a weak card knows the opponent knows it too, so betting with it never gains anything, and the best
    play is never to bet weak. Averaging over deals keeps that conclusion. But in the real game the opponent does not
    see your card; if you never bet with weak cards, your bets reveal strength and the opponent folds to them, so you
    win little. A strategy that sometimes bets weak cards (a bluff, at an equilibrium frequency) earns more, and it is
    exactly the value of hiding information that the clairvoyant model cannot represent.

??? question "12. In AlphaZero's training, why is the MCTS visit distribution π a better target for the policy head than the move actually played, and why is z (the final result) used as the value target rather than the search's own estimate?"

    $\boldsymbol{\pi}$ summarises a search guided by the current network: it combines the prior $\mathbf{p}$ with many
    lookahead evaluations, so it is usually a stronger policy than $\mathbf{p}$; training $\mathbf{p}$ towards it
    distils the search's improvement into the network (policy improvement). It is also a full distribution, giving more
    information than the single move played. The value target $z$ is the actual outcome of the game, an unbiased
    (though noisy) sample of the value of the position under the current self-play policy; using the search's own
    estimate would train the network on its own predictions, which can reinforce its errors.

## What you learned

- A two-player zero-sum game of perfect information is a game tree; its minimax value is what MAX can guarantee and
  MIN can hold MAX to, proved by induction; tic-tac-toe is a draw.
- Alpha-beta returns the minimax value exactly (and bounds outside its window), proved by induction; with perfect
  move ordering it examines $b^{\lceil d/2 \rceil} + b^{\lfloor d/2 \rfloor} - 1$ leaves, which is optimal, so ordering
  roughly doubles the reachable depth.
- Real programs cut off the search and apply an evaluation function, with quiescence search, extensions and
  transposition tables; Deep Blue (1997) was this at enormous scale.
- MCTS evaluates by random playouts and grows the tree with the UCB1 rule; UCT converges to the minimax move and needs
  no evaluation function.
- Chance nodes take expectations (expectiminimax), which makes the scale of the evaluation function matter; hidden
  information needs belief states and randomised (equilibrium) strategies, computed for poker by regret minimisation.
- AlphaGo and AlphaZero keep tree search and learn its two weak parts: a policy (which moves to search) and a value
  (how good a position is), trained from the search's own results.

**Next:** [Chapter 7](07-Constraint-Satisfaction.md), where states get internal structure (variables and constraints)
and search can exploit it.

## Further reading

- S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed., 2020: chapter 5 (adversarial search
  and games).
- C. E. Shannon, "Programming a computer for playing chess", *Philosophical Magazine* 41, 1950.
- J. von Neumann, "Zur Theorie der Gesellschaftsspiele", *Mathematische Annalen* 100, 1928; E. Zermelo, "Über eine
  Anwendung der Mengenlehre auf die Theorie des Schachspiels", 1913.
- D. E. Knuth and R. W. Moore, "An analysis of alpha-beta pruning", *Artificial Intelligence* 6, 1975; J. Pearl, "The
  solution for the branching factor of the alpha-beta pruning algorithm and its optimality", *Communications of the
  ACM* 25, 1982.
- A. L. Samuel, "Some studies in machine learning using the game of checkers", *IBM Journal of Research and
  Development* 3, 1959.
- M. Campbell, A. J. Hoane and F.-h. Hsu, "Deep Blue", *Artificial Intelligence* 134, 2002; J. Schaeffer and
  colleagues, "Checkers is solved", *Science* 317, 2007.
- P. Auer, N. Cesa-Bianchi and P. Fischer, "Finite-time analysis of the multiarmed bandit problem", *Machine Learning*
  47, 2002; L. Kocsis and C. Szepesvári, "Bandit based Monte-Carlo planning", ECML 2006; R. Coulom, "Efficient
  selectivity and backup operators in Monte-Carlo tree search", Computers and Games 2006; C. B. Browne and colleagues,
  "A survey of Monte Carlo tree search methods", *IEEE Transactions on Computational Intelligence and AI in Games* 4,
  2012.
- G. Tesauro, "Temporal difference learning and TD-Gammon", *Communications of the ACM* 38, 1995.
- M. Zinkevich, M. Johanson, M. Bowling and C. Piccione, "Regret minimization in games with incomplete information",
  NeurIPS 2007; M. Bowling, N. Burch, M. Johanson and O. Tammelin, "Heads-up limit hold'em poker is solved", *Science*
  347, 2015; N. Brown and T. Sandholm, "Superhuman AI for heads-up no-limit poker: Libratus beats top professionals",
  *Science* 359, 2018.
- D. Silver and colleagues, "Mastering the game of Go with deep neural networks and tree search", *Nature* 529, 2016;
  "Mastering the game of Go without human knowledge", *Nature* 550, 2017; "A general reinforcement learning algorithm
  that masters chess, shogi, and Go through self-play", *Science* 362, 2018; J. Schrittwieser and colleagues,
  "Mastering Atari, Go, chess and shogi by planning with a learned model", *Nature* 588, 2020.
- On this site: the Algorithms book's [Chapter 13](../algorithms/13-Dynamic-Programming.md) (memoisation, the idea
  behind transposition tables) and [Chapter 14](../algorithms/14-Backtracking-and-Branch-and-Bound.md) (pruning a
  search tree with bounds, the idea behind alpha-beta), [Depth-first search](../../graphs/dfs.md), and
  [Chapter 5](05-Local-Search-and-Optimization.md) (belief states).
