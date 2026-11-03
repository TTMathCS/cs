# 10. Union-find and range queries

*Two kinds of question come up again and again, and both look too simple to need a data structure. The first: as
connections are added one by one (cables between computers, roads between towns, friendships between people), are
these two things connected yet? The second: in a long list of numbers that keeps changing, what is the sum, or the
smallest value, between position $l$ and position $r$? Answering either by brute force costs time proportional to the
size of the data, every time. This chapter builds the structures that answer the first in nearly constant time
(union-find, with one of the strangest running times in computer science) and the second in $O(\log n)$ or even
$O(1)$ (prefix sums, Fenwick trees, segment trees and sparse tables), and proves why they work.*

!!! abstract "In this chapter"
    **You will learn:**

    - quick-find and quick-union, and why each is too slow on its own
    - union by rank and path compression, the proof that ranks stay below $\log_2 n$, the $O(\log^* n)$ amortized proof,
      and what Tarjan's inverse-Ackermann bound says
    - prefix sums and difference arrays, in one and two dimensions
    - the Fenwick tree, and where its "lowbit" trick `i & -i` comes from in binary
    - segment trees for any associative operation, and lazy propagation for range updates
    - sparse tables for range minimum in $O(1)$, and how range minimum and lowest common ancestors are the same problem

    **You need:** [Chapter 2](02-Measuring-Cost.md) (sums, logarithms), [Chapter 4](04-Lists-Stacks-and-Queues.md)
    (arrays, amortized analysis), [Chapter 8](08-Trees-and-Balanced-Search-Trees.md) (trees, depth, height). Binary
    numbers as in [math.akadian.ca](https://math.akadian.ca/books/).

    **Levels:** 10.1 and 10.3 are beginner; 10.2, 10.4 and 10.5 are intermediate; the proof in 10.2 and the second half
    of 10.6 are advanced.

## 10.1 Connectivity as you add edges

Here is the problem. There are $n$ objects, numbered $0$ to $n-1$. Connections arrive one at a time: "connect $a$ and
$b$". In between, questions arrive: "are $a$ and $b$ connected?", meaning, is there a chain of connections from $a$ to
$b$? This is the **dynamic connectivity** problem (here only with additions; deletions are much harder).

"Connected" is an **equivalence relation**: everything is connected to itself; if $a$ is connected to $b$ then $b$ is
connected to $a$; and if $a$ is connected to $b$ and $b$ to $c$, then $a$ to $c$. So the objects fall into
**disjoint sets** (the connected components), and each connection either merges two sets or does nothing. We need a
**disjoint-set** data structure, also called **union-find** after its two operations:

- **find($x$)**: return a name for the set containing $x$, the same name for every member of the set. Then "$a$ and
  $b$ are connected" is `find(a) == find(b)`.
- **union($a$, $b$)**: merge the sets containing $a$ and $b$.

The uses are everywhere: Kruskal's minimum-spanning-tree algorithm ([Chapter 17](17-Spanning-Trees-Flows-and-Matching.md))
asks for each edge whether its ends are already connected; image processing labels the connected blobs of a picture;
compilers decide which variables must share a type; physicists simulate **percolation** (when does a random grid of
open cells first connect top to bottom?). A rover team can ask the same question of a terrain map: mark each grid cell
of a Mars map as passable or not, union neighbouring passable cells, and then any two places are reachable over
passable ground exactly when they have the same find.

### Quick-find

Keep an array `id` with `id[x]` = the name of $x$'s set. Find is one lookup, $O(1)$. To union two sets, rename every
member of one set: scan the whole array, $O(n)$.

That is too slow. Connecting $n$ objects into one set takes $n - 1$ unions, so $\Theta(n^2)$ time. With a million
objects that is $10^{12}$ steps.

### Quick-union

Make the sets **trees** instead. Each object has a **parent** pointer, and the root of each tree (the object that is its
own parent) names the set.

- **find($x$)**: follow parents from $x$ until reaching a root. Cost: the depth of $x$, plus one.
- **union($a$, $b$)**: find both roots; if different, make one root the parent of the other. Cost: two finds plus
  $O(1)$.

Union is now cheap, but find costs the depth, and nothing stops the trees from becoming paths. The program's worst
case unions $1$ with $0$, then $2$ with $0$, and so on, always hanging the old root under the new object: the tree
becomes a path of length $n - 1$, and finds from its bottom cost $\Theta(n)$. In the output, 1999 unions and 2000 finds
cost quick-find 4.0 million steps and quick-union 6.0 million.

## 10.2 Union by rank, path compression, and the inverse Ackermann bound

*Level: intermediate; the proof of Theorem 10.3 is advanced.*

Two small changes fix quick-union, and together they make it one of the most efficient data structures known.

**Union by size** (or **by rank**): when linking two roots, hang the **smaller** tree under the larger one, never the
reverse. "Smaller" can mean fewer nodes (size) or a smaller **rank**, an upper bound on the height kept at each root:
a new node has rank 0; linking two roots of different rank keeps the larger rank; linking two equal ranks $r$ makes the
new root's rank $r + 1$.

**Path compression**: after a find has walked from $x$ up to the root, walk the same path again and point every node on
it straight at the root. The find costs at most twice as much as before, and every later find from those nodes takes
one step.

```python
def find(self, x):
    root = x
    while self.parent[root] != root:
        root = self.parent[root]
    while self.parent[x] != root:            # second pass
        self.parent[x], x = root, self.parent[x]
    return root

def union(self, a, b):
    ra, rb = self.find(a), self.find(b)
    if ra == rb:
        return False
    if self.rank[ra] < self.rank[rb]:
        ra, rb = rb, ra
    if self.rank[ra] == self.rank[rb]:
        self.rank[ra] += 1
    self.parent[rb] = ra
    return True
```

Here is a trace on ten objects (the program prints the parent array after each union):

| Union | Effect | Sets |
| --- | --- | --- |
| (4, 3) | equal ranks 0: 3 under 4, rank(4) = 1 | 9 |
| (3, 8) | root of 3 is 4 (rank 1) > rank(8) = 0: 8 under 4 | 8 |
| (6, 5) | 5 under 6, rank(6) = 1 | 7 |
| (9, 4) | rank(9) = 0 < rank(4) = 1: 9 under 4 | 6 |
| (2, 1) | 1 under 2, rank(2) = 1 | 5 |
| (8, 9) | both have root 4: nothing to do | 5 |
| (5, 0) | root of 5 is 6: 0 under 6 | 4 |
| (7, 2) | 7 under 2 | 3 |
| (6, 1) | roots 6 and 2, both rank 1: 2 under 6, rank(6) = 2 | 2 |

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 800 252" role="img" aria-label="Left: two trees. Root 6 has children 5, 0 and 2; node 2 has children 1 and 7. Root 4 has children 3, 8 and 9. Right: a path x to b to a to root r becomes, after find of x, three nodes a, b and x all pointing directly at r.">
<line x1="110" y1="50" x2="40" y2="120" stroke="currentColor" stroke-width="1.5"/>
<line x1="110" y1="50" x2="110" y2="120" stroke="currentColor" stroke-width="1.5"/>
<line x1="110" y1="50" x2="180" y2="120" stroke="currentColor" stroke-width="1.5"/>
<line x1="180" y1="120" x2="150" y2="190" stroke="currentColor" stroke-width="1.5"/>
<line x1="180" y1="120" x2="210" y2="190" stroke="currentColor" stroke-width="1.5"/>
<line x1="330" y1="50" x2="270" y2="120" stroke="currentColor" stroke-width="1.5"/>
<line x1="330" y1="50" x2="330" y2="120" stroke="currentColor" stroke-width="1.5"/>
<line x1="330" y1="50" x2="390" y2="120" stroke="currentColor" stroke-width="1.5"/>
<circle cx="110" cy="50" r="17" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/><text x="110" y="55" font-size="14" text-anchor="middle" fill="currentColor">6</text>
<circle cx="40" cy="120" r="17" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/><text x="40" y="125" font-size="14" text-anchor="middle" fill="currentColor">5</text>
<circle cx="110" cy="120" r="17" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/><text x="110" y="125" font-size="14" text-anchor="middle" fill="currentColor">0</text>
<circle cx="180" cy="120" r="17" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/><text x="180" y="125" font-size="14" text-anchor="middle" fill="currentColor">2</text>
<circle cx="150" cy="190" r="17" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/><text x="150" y="195" font-size="14" text-anchor="middle" fill="currentColor">1</text>
<circle cx="210" cy="190" r="17" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/><text x="210" y="195" font-size="14" text-anchor="middle" fill="currentColor">7</text>
<circle cx="330" cy="50" r="17" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/><text x="330" y="55" font-size="14" text-anchor="middle" fill="currentColor">4</text>
<circle cx="270" cy="120" r="17" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/><text x="270" y="125" font-size="14" text-anchor="middle" fill="currentColor">3</text>
<circle cx="330" cy="120" r="17" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/><text x="330" y="125" font-size="14" text-anchor="middle" fill="currentColor">8</text>
<circle cx="390" cy="120" r="17" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/><text x="390" y="125" font-size="14" text-anchor="middle" fill="currentColor">9</text>
<text x="220" y="236" font-size="12" text-anchor="middle" fill="currentColor">(a) after the nine unions: two sets, roots 6 and 4</text>
<line x1="510" y1="40" x2="510" y2="95" stroke="currentColor" stroke-width="1.5"/>
<line x1="510" y1="95" x2="510" y2="150" stroke="currentColor" stroke-width="1.5"/>
<line x1="510" y1="150" x2="510" y2="205" stroke="currentColor" stroke-width="1.5"/>
<circle cx="510" cy="40" r="17" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/><text x="510" y="45" font-size="14" text-anchor="middle" fill="currentColor">r</text>
<circle cx="510" cy="95" r="17" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/><text x="510" y="100" font-size="14" text-anchor="middle" fill="currentColor">a</text>
<circle cx="510" cy="150" r="17" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/><text x="510" y="155" font-size="14" text-anchor="middle" fill="currentColor">b</text>
<circle cx="510" cy="205" r="17" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/><text x="510" y="210" font-size="14" text-anchor="middle" fill="currentColor">x</text>
<line x1="555" y1="120" x2="601.0" y2="120.0" stroke="currentColor" stroke-width="1.5"/><polygon points="610,120 601.0,124.0 601.0,116.0" fill="currentColor"/>
<text x="582" y="110" font-size="11" text-anchor="middle" fill="currentColor">find(x)</text>
<line x1="700" y1="50" x2="640" y2="130" stroke="currentColor" stroke-width="1.5"/>
<line x1="700" y1="50" x2="700" y2="130" stroke="currentColor" stroke-width="1.5"/>
<line x1="700" y1="50" x2="760" y2="130" stroke="currentColor" stroke-width="1.5"/>
<circle cx="700" cy="50" r="17" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/><text x="700" y="55" font-size="14" text-anchor="middle" fill="currentColor">r</text>
<circle cx="640" cy="130" r="17" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/><text x="640" y="135" font-size="14" text-anchor="middle" fill="currentColor">a</text>
<circle cx="700" cy="130" r="17" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/><text x="700" y="135" font-size="14" text-anchor="middle" fill="currentColor">b</text>
<circle cx="760" cy="130" r="17" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/><text x="760" y="135" font-size="14" text-anchor="middle" fill="currentColor">x</text>
<text x="630" y="236" font-size="12" text-anchor="middle" fill="currentColor">(b) path compression: all now point at the root</text>
</svg>
<figcaption>Figure 10.1. Union-find stores each set as a tree of parent pointers; the root names the set. (a) The forest after the trace in section 10.2. (b) Path compression: a find walks to the root, then points every node it passed straight at the root, so the next find from any of them takes one step.</figcaption>
</figure>

### Union by rank alone: logarithmic height

Ranks have three properties that we use below, with or without path compression.

1. **Ranks increase going up**: if $p$ is the parent of $x$ then rank($p$) > rank($x$). (When $x$ is linked under $p$,
   rank($p$) $\ge$ rank($x$), and strictly more if they were equal, because then rank($p$) goes up. Path compression
   only makes $x$ point at an ancestor, whose rank is even larger.)
2. **A non-root's rank never changes** (only roots are linked and incremented).
3. **Size**: a root of rank $r$ has at least $2^r$ nodes in its tree.

*Proof of 3,* by induction on the number of unions. A new node has rank 0 and size $1 = 2^0$. A union that does not
change the larger rank only adds nodes. A union of two roots of equal rank $r$ makes a tree with at least
$2^r + 2^r = 2^{r+1}$ nodes and rank $r + 1$. (Path compression changes no root's tree size.) $\square$

**Lemma 10.1.** With union by rank, every rank is at most $\lfloor\log_2 n\rfloor$, and at most $n/2^r$ nodes ever have
rank $r$.

*Proof.* A root of rank $r$ has at least $2^r$ nodes, and there are only $n$, so $2^r \le n$. For the second part,
when a node reaches rank $r$, label it with the $2^r$ or more nodes of its tree at that moment. No node $y$ gets two
labels from different nodes $x$ and $z$ of rank $r$: say $z$ reached rank $r$ after $x$ did. Trees only ever merge, so
at that moment $y$ and $x$ are in $z$'s tree, with $x$ on the path from $y$ up to the root $z$. Then $z$ is a proper
ancestor of $x$ and, by property 1, rank($z$) $>$ rank($x$) $= r$, a contradiction. So the labelled sets are disjoint,
and there are at most $n/2^r$ of them. $\square$

Without path compression, rank bounds height (property 1 plus the fact that a rank-0 node is a leaf), so **every find
costs $O(\log n)$**, and so does every union. The bound is tight: joining equal-sized trees in pairs, as in the
program, builds a tree in which the deepest find takes exactly $\log_2 n$ steps (11 for $n = 2048$).

### Path compression on top: $O(\log^* n)$

The **iterated logarithm** $\log^* n$ is the number of times you must apply $\log_2$ to $n$ before the result is at
most 1. So $\log^* 2 = 1$, $\log^* 16 = 3$ ($16 \to 4 \to 2 \to 1$), $\log^* 65536 = 4$, and $\log^* 2^{65536} = 5$.
Since $2^{65536}$ has nearly 20,000 decimal digits, $\log^* n \le 5$ for any $n$ you will ever store.

**Theorem 10.2** (Hopcroft and Ullman 1973). With union by rank and path compression, any sequence of $m$ finds and
unions on $n$ objects takes $O((m + n)\log^* n)$ time.

*Proof.* Unions cost two finds plus $O(1)$, so count the cost of finds: the number of nodes on each find path.

Group the ranks into **blocks**. Let $T(0) = 1$ and $T(j) = 2^{T(j-1)}$ (a tower of $j$ twos:
$1, 2, 4, 16, 65536, \dots$). Block 0 holds ranks 0 and 1; block $j \ge 1$ holds the ranks $r$ with $T(j-1) < r \le T(j)$. Ranks are at most
$\log_2 n$, so only about $\log^* n + 1$ blocks are used.

On a find path $x_1, x_2, \dots, x_k$ (with $x_k$ the root), charge each node $x_i$ as follows:

- if $x_i$ is the root or the root's child, or its parent's rank is in a **different block** from its own rank, charge
  1 to **the find itself**;
- otherwise (parent in the **same block**), charge 1 to **the node** $x_i$.

*Charges to finds.* Along the path ranks strictly increase (property 1), so the block number changes at most once per
block: at most $\log^* n + 1$ times. With the root and its child, each find is charged $O(\log^* n)$, for
$O(m\log^* n)$ in all.

*Charges to nodes.* Take a node $x$ in block $j$, so $T(j-1) < \mathrm{rank}(x) \le T(j)$; its rank no longer changes
(property 2; it is not a root, since it has a parent). Each time $x$ is charged, its parent is not the root, so path
compression gives $x$ a new parent: the root, whose rank is strictly larger than the old parent's (property 1). So the
parent's rank goes up by at least 1 with every charge. Once it passes $T(j)$, the parent is in a higher block and $x$
is never charged again. The parent's rank starts above rank($x$) $> T(j-1)$, so $x$ is charged at most $T(j)$ times.

How many nodes are in block $j$? By Lemma 10.1, at most

$$
\sum_{r > T(j-1)} \frac{n}{2^r} \le \frac{n}{2^{T(j-1)}} = \frac{n}{T(j)} .
$$

So all nodes in block $j$ together are charged at most $\frac{n}{T(j)}\cdot T(j) = n$. Over the $\log^* n + 1$ blocks
that is $O(n\log^* n)$. Adding the two kinds of charges proves the theorem. $\square$

### The true bound: inverse Ackermann

$\log^* n$ is not the end. Robert Tarjan proved in 1975 ("Efficiency of a good but not linear set union algorithm",
*Journal of the ACM*) that the cost is $O(m\,\alpha(m, n))$, where $\alpha$ is an **inverse of Ackermann's function**.
Ackermann's function grows so fast that towers of twos are slow by comparison; one common version is

$$
A_0(j) = j + 1, \qquad A_{k}(j) = A_{k-1}^{(j+1)}(j) \text{ for } k \ge 1,
$$

where $A^{(j+1)}$ means "apply $j + 1$ times". Then $A_1(j) = 2j + 1$, $A_2(j) = 2^{j+1}(j+1) - 1$, $A_3$ is already a
tower, and $A_4(1)$ is far larger than $10^{80}$, the usual estimate of the number of atoms in the observable universe.
The inverse $\alpha(n)$ is the smallest $k$ with $A_k(1) \ge n$, so $\alpha(n) \le 4$ for every $n$ up to $A_4(1)$.
CLRS (chapter 19 of the 4th edition) gives a complete proof of the $O(m\,\alpha(n))$ bound with a potential function.

And it is not just a weakness of the proof. Tarjan (1979) showed that a broad class of pointer-based algorithms needs
$\Omega(m\,\alpha(m, n))$ time, and Fredman and Saks (1989) proved the same lower bound in the **cell-probe model**,
which counts only memory accesses and so applies to any algorithm. So union-find takes **more than constant** time per
operation, but only by a factor that never exceeds 4 or so on this planet or any other. This is one of the rare
problems where the exact complexity, a strange function, is known.

**History.** Bernard Galler and Michael Fischer introduced the tree representation in 1964 ("An improved equivalence
algorithm", *Communications of the ACM*). Path compression was folklore in the 1960s; Hopcroft and Ullman's 1973 paper
gave the $\log^*$ bound; Tarjan's 1975 paper gave the inverse-Ackermann bound; Tarjan and van Leeuwen (1984) analysed
the one-pass variants **path halving** (point every other node at its grandparent) and **path splitting**, which have
the same bound and avoid the second pass.

```python
--8<-- "books/algorithms/ch10_union_find.py"
```

```
union(4,3) merged   parent = [0, 1, 2, 4, 4, 5, 6, 7, 8, 9]  sets = 9
union(3,8) merged   parent = [0, 1, 2, 4, 4, 5, 6, 7, 4, 9]  sets = 8
union(6,5) merged   parent = [0, 1, 2, 4, 4, 6, 6, 7, 4, 9]  sets = 7
union(9,4) merged   parent = [0, 1, 2, 4, 4, 6, 6, 7, 4, 4]  sets = 6
union(2,1) merged   parent = [0, 2, 2, 4, 4, 6, 6, 7, 4, 4]  sets = 5
union(8,9) already   parent = [0, 2, 2, 4, 4, 6, 6, 7, 4, 4]  sets = 5
union(5,0) merged   parent = [6, 2, 2, 4, 4, 6, 6, 7, 4, 4]  sets = 4
union(7,2) merged   parent = [6, 2, 2, 4, 4, 6, 6, 2, 4, 4]  sets = 3
union(6,1) merged   parent = [6, 2, 6, 4, 4, 6, 6, 2, 4, 4]  sets = 2
connected(0, 7): True   connected(0, 4): False
quick-find       1999 unions + 2000 finds of 0:  4003998 steps
quick-union      1999 unions + 2000 finds of 0:  5995001 steps
by rank only     1999 unions + 2000 finds of 0:     3998 steps
compress only    1999 unions + 2000 finds of 0:     5996 steps
rank + compress  1999 unions + 2000 finds of 0:     3998 steps
by rank only, n = 2048 joined in equal pairs: find(2047) takes 11 steps = log2 n
n = 200000, 200000 random unions: 32343 sets left, max rank 7, log2 n = 17.6
nodes of rank r: [151001, 38923, 8351, 1462, 223, 36, 3, 1]  bound n/2^r: [200000, 100000, 50000, 25000, 12500, 6250, 3125, 1562]
log* of 2, 16, 65536, 10**80: [1, 3, 4, 5]
```

The rank counts on 200,000 random unions stay well under the $n/2^r$ bound of Lemma 10.1, and the largest rank, 7, is
far below $\log_2 n \approx 17.6$. The [union-find reference page](../../data-structures/union-find.md) has the same
structure in Java and C++ with an animation.

## 10.3 Prefix sums and difference arrays

Now the second kind of question. A list $a_0, a_1, \dots, a_{n-1}$ of numbers is given, and many queries ask for
$a_l + a_{l+1} + \dots + a_{r-1}$. (We use **half-open ranges** $[l, r)$: $l$ included, $r$ excluded, as Python's
slices do. The range has $r - l$ elements, and $[l, m)$ and $[m, r)$ fit together with no overlap.) Adding up each
range costs $O(r - l)$. Can we do better?

**Prefix sums.** Compute once $p_0 = 0$ and $p_{i+1} = p_i + a_i$, so that $p_i = a_0 + \dots + a_{i-1}$ is the sum of
the first $i$ elements. Then

$$
a_l + \dots + a_{r-1} = p_r - p_l ,
$$

because $p_r$ adds up everything before $r$ and $p_l$ everything before $l$; the difference is exactly the range. The
table costs $O(n)$ to build and each query $O(1)$. With $a = [3, 1, 4, 1, 5, 9, 2, 6]$ the prefix sums are
$[0, 3, 4, 8, 9, 14, 23, 25, 31]$ and the sum of $a_2, \dots, a_5$ is $p_6 - p_2 = 23 - 4 = 19$.

The trick needs **subtraction**: it works for sums, for counts, for XOR (which is its own inverse), and for products of
nonzero numbers, but not for minimum or maximum, which cannot be "undone". Section 10.6 handles those.

**Difference arrays** run the idea backwards. Suppose many updates say "add $v$ to every element of $[l, r)$" and only
at the end do we need the array. Keep $d$ with $d_l \mathrel{+}= v$ and $d_r \mathrel{-}= v$ for each update; at the end
the prefix sums of $d$ are the array. *Why:* the prefix sum at position $i$ adds every $v$ whose $l \le i$ and subtracts
every $v$ whose $r \le i$, so it counts exactly the updates with $l \le i < r$. Each update is $O(1)$ and the final pass
$O(n)$. Starting from eight zeros, "add 10 to $[1, 4)$" and "add 5 to $[2, 7)$" give $d = [0, 10, 5, 0, -10, 0, 0, -5]$,
whose prefix sums are $[0, 10, 15, 15, 5, 5, 5, 0]$.

**Two dimensions.** For a grid $g$, let $P_{i,j}$ be the sum of the rectangle of rows $0..i-1$ and columns $0..j-1$.
By **inclusion-exclusion** (add the two overlapping strips, subtract the part counted twice),

$$
P_{i+1,j+1} = g_{i,j} + P_{i,j+1} + P_{i+1,j} - P_{i,j},
$$

and the sum of any rectangle, rows $[r_1, r_2)$ and columns $[c_1, c_2)$, is
$P_{r_2,c_2} - P_{r_1,c_2} - P_{r_2,c_1} + P_{r_1,c_1}$: four lookups. Image processing calls $P$ a **summed-area
table** or **integral image**; Viola and Jones's face detector (2001) used it to add up rectangles of pixels in
constant time.

Prefix sums are perfect when the array never changes. When it does, one update to $a_i$ changes every $p_j$ with
$j > i$, which is $O(n)$. The next two structures balance the two costs.

## 10.4 Fenwick trees

*Level: intermediate.*

We want both "add $v$ to $a_i$" and "sum of $a_1, \dots, a_i$" in $O(\log n)$. (Fenwick trees are traditionally
**1-based**: positions $1$ to $n$. A range sum $[l, r]$ is then prefix($r$) $-$ prefix($l - 1$).)

Peter Fenwick described the structure in 1994 ("A new data structure for cumulative frequency tables",
*Software: Practice and Experience*), for the frequency counts of an arithmetic coder in data compression; a closely
related structure had been described by Boris Ryabko in 1989. It is also called a **binary indexed tree**. It is one
array of $n$ numbers, the same size as the data.

### The lowbit trick, from binary

For a positive integer $i$, let **lowbit($i$)** be the value of its lowest 1-bit: lowbit$(12) = 4$ because
$12 = 1100_2$, lowbit$(7) = 1$, lowbit$(8) = 8$. In code it is `i & -i`. *Why that works:* computers store $-i$ in
**two's complement**, which is $\lnot i + 1$ (flip every bit, then add 1). Write $i = \dots x\,1\,0\cdots0$, with
$k$ zeros after the lowest 1-bit. Flipping gives $\dots \bar x\,0\,1\cdots1$; adding 1 turns the $k$ ones back into
zeros and carries into the 0, giving $\dots\bar x\,1\,0\cdots0$. So $-i$ agrees with $i$ on the lowest 1-bit and the
zeros below it, and is the opposite of $i$ on every bit above. AND-ing them leaves exactly the lowest 1-bit. (Python's
integers behave as if they had infinitely many bits in two's complement, so `i & -i` works there too.)

**The tree:** entry $t_i$ stores the sum of the lowbit$(i)$ elements that **end at** $i$:

$$
t_i = a_{i - \mathrm{lowbit}(i) + 1} + \dots + a_i .
$$

So $t_1 = a_1$, $t_2 = a_1 + a_2$, $t_3 = a_3$, $t_4 = a_1 + \dots + a_4$, $t_6 = a_5 + a_6$, $t_8 = a_1 + \dots + a_8$.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 700 262" role="img" aria-label="The array a with values 3, 1, 4, 1, 5, 9, 2, 6 at positions 1 to 8. Below it, bars show which positions each Fenwick entry covers: t1, t3, t5, t7 cover one position; t2 and t6 two; t4 four; t8 all eight. t7, t6 and t4 are highlighted.">
<rect x="120" y="20" width="70" height="30" rx="0" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="155.0" y="41" font-size="14" text-anchor="middle" fill="currentColor">3</text>
<text x="155.0" y="66" font-size="11" text-anchor="middle" fill="currentColor">a[1]</text>
<rect x="190" y="20" width="70" height="30" rx="0" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="225.0" y="41" font-size="14" text-anchor="middle" fill="currentColor">1</text>
<text x="225.0" y="66" font-size="11" text-anchor="middle" fill="currentColor">a[2]</text>
<rect x="260" y="20" width="70" height="30" rx="0" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="295.0" y="41" font-size="14" text-anchor="middle" fill="currentColor">4</text>
<text x="295.0" y="66" font-size="11" text-anchor="middle" fill="currentColor">a[3]</text>
<rect x="330" y="20" width="70" height="30" rx="0" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="365.0" y="41" font-size="14" text-anchor="middle" fill="currentColor">1</text>
<text x="365.0" y="66" font-size="11" text-anchor="middle" fill="currentColor">a[4]</text>
<rect x="400" y="20" width="70" height="30" rx="0" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="435.0" y="41" font-size="14" text-anchor="middle" fill="currentColor">5</text>
<text x="435.0" y="66" font-size="11" text-anchor="middle" fill="currentColor">a[5]</text>
<rect x="470" y="20" width="70" height="30" rx="0" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="505.0" y="41" font-size="14" text-anchor="middle" fill="currentColor">9</text>
<text x="505.0" y="66" font-size="11" text-anchor="middle" fill="currentColor">a[6]</text>
<rect x="540" y="20" width="70" height="30" rx="0" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="575.0" y="41" font-size="14" text-anchor="middle" fill="currentColor">2</text>
<text x="575.0" y="66" font-size="11" text-anchor="middle" fill="currentColor">a[7]</text>
<rect x="610" y="20" width="70" height="30" rx="0" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="645.0" y="41" font-size="14" text-anchor="middle" fill="currentColor">6</text>
<text x="645.0" y="66" font-size="11" text-anchor="middle" fill="currentColor">a[8]</text>
<text x="10" y="41" font-size="12" text-anchor="start" fill="currentColor">array a</text>
<rect x="124" y="200" width="62" height="24" rx="4" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<text x="155.0" y="217" font-size="12" text-anchor="middle" fill="currentColor">t[1] = 3</text>
<rect x="124" y="166" width="132" height="24" rx="4" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<text x="190.0" y="183" font-size="12" text-anchor="middle" fill="currentColor">t[2] = 4</text>
<rect x="264" y="200" width="62" height="24" rx="4" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<text x="295.0" y="217" font-size="12" text-anchor="middle" fill="currentColor">t[3] = 4</text>
<rect x="124" y="132" width="272" height="24" rx="4" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/>
<text x="260.0" y="149" font-size="12" text-anchor="middle" fill="currentColor">t[4] = 9</text>
<rect x="404" y="200" width="62" height="24" rx="4" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<text x="435.0" y="217" font-size="12" text-anchor="middle" fill="currentColor">t[5] = 5</text>
<rect x="404" y="166" width="132" height="24" rx="4" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/>
<text x="470.0" y="183" font-size="12" text-anchor="middle" fill="currentColor">t[6] = 14</text>
<rect x="544" y="200" width="62" height="24" rx="4" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/>
<text x="575.0" y="217" font-size="12" text-anchor="middle" fill="currentColor">t[7] = 2</text>
<rect x="124" y="98" width="552" height="24" rx="4" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<text x="400.0" y="115" font-size="12" text-anchor="middle" fill="currentColor">t[8] = 31</text>
<text x="10" y="217" font-size="12" text-anchor="start" fill="currentColor">lowbit 1</text>
<text x="10" y="183" font-size="12" text-anchor="start" fill="currentColor">lowbit 2</text>
<text x="10" y="149" font-size="12" text-anchor="start" fill="currentColor">lowbit 4</text>
<text x="10" y="115" font-size="12" text-anchor="start" fill="currentColor">lowbit 8</text>
<text x="400" y="250" font-size="12" text-anchor="middle" fill="currentColor">prefix(7) = t[7] + t[6] + t[4] = 2 + 14 + 9 = 25   (7 = 111, 6 = 110, 4 = 100 in binary)</text>
</svg>
<figcaption>Figure 10.2. A Fenwick tree on eight values. Entry t[i] stores the sum of the lowbit(i) values ending at position i, where lowbit(i) is the value of the lowest 1-bit of i. A prefix sum adds one entry per 1-bit: the highlighted bars t[7], t[6], t[4] tile positions 1 to 7 exactly.</figcaption>
</figure>

**Prefix sum:** to add up $a_1, \dots, a_i$, take $t_i$ (which covers $(i - \mathrm{lowbit}(i), i]$), then continue
from $i - \mathrm{lowbit}(i)$, until reaching 0:

```python
def prefix(self, i):
    s = 0
    while i > 0:
        s += self.t[i]
        i -= i & -i          # clear the lowest 1-bit
    return s
```

*Correctness:* the ranges $(i - \mathrm{lowbit}(i), i]$, then $(i', i]$ for $i' = i - \mathrm{lowbit}(i)$ and so on,
fit end to end and stop at 0, so they tile $[1, i]$ exactly. *Cost:* each step clears one 1-bit of $i$, so the number
of steps is the number of 1-bits, at most $\lfloor\log_2 n\rfloor + 1$. For $i = 7 = 111_2$ it reads $t_7, t_6, t_4$:
$2 + 14 + 9 = 25 = a_1 + \dots + a_7$.

**Update:** to add $v$ to $a_i$, add it to every $t_j$ whose range contains $i$. Those are found by **adding** the
lowbit instead:

```python
def add(self, i, v):
    while i <= self.n:
        self.t[i] += v
        i += i & -i
```

*Correctness.* Which $j$ cover position $i$? Certainly $j = i$. For $j > i$, $t_j$ covers $(j - 2^k, j]$ where
$2^k = \mathrm{lowbit}(j)$, and $i$ lies in it exactly when $i$ agrees with $j$ on every bit above bit $k$, has a 0
at bit $k$ (where $j$ has its 1), and has some 1-bit below $k$ (so that $i > j - 2^k$). So the covering $j$ are: for
each 0-bit of $i$ at a position $k$ above lowbit($i$), the number made by setting bit $k$ and clearing everything
below. Adding lowbit($i$) to $i$ does exactly that for the *lowest* such 0-bit (the carry runs through the block of
1s ending at the lowbit, clearing it, and stops at the first 0, setting it). Repeating gives the next one up. So the
loop visits exactly the covering entries, in increasing order, and each step moves the lowest 1-bit up by at least one
place: $O(\log n)$ steps. For $i = 3 = 011_2$ it writes $t_3, t_4, t_8$, which are the three bars over position 3
in Figure 10.2.

**Building** in $O(n)$: set $t_i = a_i$, then for $i = 1$ to $n$ add $t_i$ into $t_{i + \mathrm{lowbit}(i)}$ (its
"parent", the next entry covering it). Each entry is finished before it is passed on, because its parent has a larger
index.

```python
--8<-- "books/algorithms/ch10_prefix_fenwick.py"
```

```
a          : [3, 1, 4, 1, 5, 9, 2, 6]
prefix sums: [0, 3, 4, 8, 9, 14, 23, 25, 31]
sum a[2..5] = 19
difference array, add 10 to a[1..3] and 5 to a[2..6] on zeros: [0, 10, 15, 15, 5, 5, 5, 0]
2D: sum of the bottom-right 2x2 block = 28
 i  binary  lowbit  t[i] covers
 1  0001     1     a[1..1]
 2  0010     2     a[1..2]
 3  0011     1     a[3..3]
 4  0100     4     a[1..4]
 5  0101     1     a[5..5]
 6  0110     2     a[5..6]
 7  0111     1     a[7..7]
 8  1000     8     a[1..8]
tree t[1..8]: [3, 4, 4, 9, 5, 14, 2, 31]
prefix(7) reads t at [7, 6, 4] = 25
add(3, ...) writes t at [3, 4, 8]
20000 random adds and range sums on n = 100000 agree with brute force: True
```

(The first part of the program uses 0-based positions like Python lists; the Fenwick part is 1-based.)

**Variations.** Store a difference array in the Fenwick tree and you get **range add, point query**: add $v$ at $l$
and $-v$ at $r + 1$; the value of $a_i$ is prefix($i$). With **two** Fenwick trees you get range add *and* range sum
(exercise 9). A Fenwick tree over value ranks counts **inversions** in $O(n\log n)$ (exercise 12). There are 2D Fenwick
trees for grids, and a Fenwick tree can find the smallest $i$ with prefix($i$) $\ge s$ in $O(\log n)$ by walking down
the powers of two. What it cannot do directly is minimum over an arbitrary range, because it relies on subtraction:
for that we need the segment tree. The [Fenwick tree reference page](../../data-structures/fenwick-tree.md) has an
animation of the update and query paths.

## 10.5 Segment trees and lazy propagation

*Level: intermediate.*

A **segment tree** answers range queries for **any associative operation** $\oplus$ (one with
$(x\oplus y)\oplus z = x\oplus(y\oplus z)$): sum, minimum, maximum, gcd, product of matrices, "the leftmost position
above a threshold", and many more. It does not need an inverse.

**Structure.** A complete binary tree over the positions. The root covers $[0, n)$; a node covering $[lo, hi)$ with
$hi - lo \ge 2$ has a left child covering $[lo, mid)$ and a right child covering $[mid, hi)$, where
$mid = \lfloor (lo + hi)/2 \rfloor$; a leaf covers one position. Every node stores the $\oplus$ of its range. Stored in
an array the way a heap is ([Chapter 9](09-Heaps-and-Priority-Queues.md)), node $v$ has children $2v$ and $2v + 1$,
with the root at 1. The tree has fewer than $2n$ nodes, but when $n$ is not a power of two the indices can reach
almost $4n$, so code allocates $4n$ slots.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 760 276" role="img" aria-label="A segment tree over 8 values 5, 8, 6, 3, 2, 7, 2, 6. Each node shows the minimum of its range: root [0,8) holds 2; [0,4) holds 3 and [4,8) holds 2; and so on to the leaves. The nodes for [1,2), [2,4) and [4,6) are highlighted.">
<line x1="380.0" y1="40" x2="220.0" y2="100" stroke="currentColor" stroke-width="1.5"/>
<line x1="380.0" y1="40" x2="540.0" y2="100" stroke="currentColor" stroke-width="1.5"/>
<line x1="220.0" y1="100" x2="140.0" y2="160" stroke="currentColor" stroke-width="1.5"/>
<line x1="220.0" y1="100" x2="300.0" y2="160" stroke="currentColor" stroke-width="1.5"/>
<line x1="540.0" y1="100" x2="460.0" y2="160" stroke="currentColor" stroke-width="1.5"/>
<line x1="540.0" y1="100" x2="620.0" y2="160" stroke="currentColor" stroke-width="1.5"/>
<line x1="140.0" y1="160" x2="100.0" y2="220" stroke="currentColor" stroke-width="1.5"/>
<line x1="140.0" y1="160" x2="180.0" y2="220" stroke="currentColor" stroke-width="1.5"/>
<line x1="300.0" y1="160" x2="260.0" y2="220" stroke="currentColor" stroke-width="1.5"/>
<line x1="300.0" y1="160" x2="340.0" y2="220" stroke="currentColor" stroke-width="1.5"/>
<line x1="460.0" y1="160" x2="420.0" y2="220" stroke="currentColor" stroke-width="1.5"/>
<line x1="460.0" y1="160" x2="500.0" y2="220" stroke="currentColor" stroke-width="1.5"/>
<line x1="620.0" y1="160" x2="580.0" y2="220" stroke="currentColor" stroke-width="1.5"/>
<line x1="620.0" y1="160" x2="660.0" y2="220" stroke="currentColor" stroke-width="1.5"/>
<rect x="354.0" y="25" width="52" height="30" rx="6" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="380.0" y="41" font-size="13" text-anchor="middle" fill="currentColor">2</text>
<text x="380.0" y="52" font-size="9" text-anchor="middle" fill="currentColor">[0,8)</text>
<rect x="194.0" y="85" width="52" height="30" rx="6" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="220.0" y="101" font-size="13" text-anchor="middle" fill="currentColor">3</text>
<text x="220.0" y="112" font-size="9" text-anchor="middle" fill="currentColor">[0,4)</text>
<rect x="514.0" y="85" width="52" height="30" rx="6" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="540.0" y="101" font-size="13" text-anchor="middle" fill="currentColor">2</text>
<text x="540.0" y="112" font-size="9" text-anchor="middle" fill="currentColor">[4,8)</text>
<rect x="114.0" y="145" width="52" height="30" rx="6" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="140.0" y="161" font-size="13" text-anchor="middle" fill="currentColor">5</text>
<text x="140.0" y="172" font-size="9" text-anchor="middle" fill="currentColor">[0,2)</text>
<rect x="274.0" y="145" width="52" height="30" rx="6" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/>
<text x="300.0" y="161" font-size="13" text-anchor="middle" fill="currentColor">3</text>
<text x="300.0" y="172" font-size="9" text-anchor="middle" fill="currentColor">[2,4)</text>
<rect x="434.0" y="145" width="52" height="30" rx="6" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/>
<text x="460.0" y="161" font-size="13" text-anchor="middle" fill="currentColor">2</text>
<text x="460.0" y="172" font-size="9" text-anchor="middle" fill="currentColor">[4,6)</text>
<rect x="594.0" y="145" width="52" height="30" rx="6" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="620.0" y="161" font-size="13" text-anchor="middle" fill="currentColor">2</text>
<text x="620.0" y="172" font-size="9" text-anchor="middle" fill="currentColor">[6,8)</text>
<rect x="74.0" y="205" width="52" height="30" rx="6" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<text x="100.0" y="221" font-size="13" text-anchor="middle" fill="currentColor">5</text>
<text x="100.0" y="232" font-size="9" text-anchor="middle" fill="currentColor">[0,1)</text>
<rect x="154.0" y="205" width="52" height="30" rx="6" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/>
<text x="180.0" y="221" font-size="13" text-anchor="middle" fill="currentColor">8</text>
<text x="180.0" y="232" font-size="9" text-anchor="middle" fill="currentColor">[1,2)</text>
<rect x="234.0" y="205" width="52" height="30" rx="6" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<text x="260.0" y="221" font-size="13" text-anchor="middle" fill="currentColor">6</text>
<text x="260.0" y="232" font-size="9" text-anchor="middle" fill="currentColor">[2,3)</text>
<rect x="314.0" y="205" width="52" height="30" rx="6" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<text x="340.0" y="221" font-size="13" text-anchor="middle" fill="currentColor">3</text>
<text x="340.0" y="232" font-size="9" text-anchor="middle" fill="currentColor">[3,4)</text>
<rect x="394.0" y="205" width="52" height="30" rx="6" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<text x="420.0" y="221" font-size="13" text-anchor="middle" fill="currentColor">2</text>
<text x="420.0" y="232" font-size="9" text-anchor="middle" fill="currentColor">[4,5)</text>
<rect x="474.0" y="205" width="52" height="30" rx="6" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<text x="500.0" y="221" font-size="13" text-anchor="middle" fill="currentColor">7</text>
<text x="500.0" y="232" font-size="9" text-anchor="middle" fill="currentColor">[5,6)</text>
<rect x="554.0" y="205" width="52" height="30" rx="6" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<text x="580.0" y="221" font-size="13" text-anchor="middle" fill="currentColor">2</text>
<text x="580.0" y="232" font-size="9" text-anchor="middle" fill="currentColor">[6,7)</text>
<rect x="634.0" y="205" width="52" height="30" rx="6" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<text x="660.0" y="221" font-size="13" text-anchor="middle" fill="currentColor">6</text>
<text x="660.0" y="232" font-size="9" text-anchor="middle" fill="currentColor">[7,8)</text>
<text x="380" y="262" font-size="12" text-anchor="middle" fill="currentColor">min of a[1:6]: the three orange nodes cover [1,2), [2,4), [4,6); answer min(8, 3, 2) = 2</text>
</svg>
<figcaption>Figure 10.3. A segment tree for range minimum. Each node stores the minimum of a half-open range [lo, hi), and its children split the range in half. A query is answered by a few nodes that fit inside it exactly.</figcaption>
</figure>

- **Build**: recursively build both children, then combine. Each node once: $O(n)$.
- **Point update** $a_i = x$: go down to leaf $i$, set it, and recompute each node on the way back up. $O(\log n)$.
- **Query** $[l, r)$ from a node covering $[lo, hi)$: if the ranges do not overlap, return the identity (0 for sum,
  $+\infty$ for min); if $[lo, hi) \subseteq [l, r)$, return the stored value; otherwise ask both children and combine.

**Theorem 10.3.** A segment-tree query visits at most 4 nodes per level, so $O(\log n)$ nodes.

*Proof.* Call a visited node **partial** if its range overlaps the query but is not inside it; only partial nodes have
their children visited. A partial node's range contains $l$ or $r$ in its interior, i.e., it contains one of the two
"cut points" of the query: if it contained neither, it would lie entirely inside or entirely outside $[l, r)$. The
ranges of the nodes on one level are disjoint, so at most two nodes per level are partial (one containing each cut
point). Hence at most $2 \times 2 = 4$ nodes are visited on the next level. With $\lceil\log_2 n\rceil + 1$ levels, the
query visits $O(\log n)$ nodes. $\square$

In Figure 10.3 the query $[1, 6)$ for the minimum of $8, 6, 3, 2, 7$ uses three nodes, $[1,2)$, $[2,4)$ and $[4,6)$,
with stored values 8, 3 and 2; the answer is 2. The program's random test never visited more than 59 nodes for one
query with $n = 50000$, against the bound $4\log_2 n \approx 62$.

### Lazy propagation: range updates

Now let the *updates* be ranges too: "add $x$ to every element of $[l, r)$". Doing it leaf by leaf costs $O(r - l)$.
The trick is to be **lazy**: when an update covers a node's whole range, update the node's own sum (add $x$ times the
length) and write a **tag** `lazy[v] += x` meaning "my children have not been told about this yet". Stop there. Only when
a later operation needs to go *below* $v$, **push** the tag down: apply it to both children (to their sums and their
tags) and clear it at $v$.

**Invariant:** for every node $v$, the stored sum $s_v$ equals the true sum of $v$'s range, except for adds recorded in
the tags of $v$'s proper ancestors and not yet pushed down to $v$. At the root there are no ancestors, so its sum is
always right. An operation that stops at $v$ (fully inside the range) can read $s_v$ because it pushed every tag on the
path from the root to $v$ on the way down. Updating a fully covered node updates its sum and its tag together, so its
children's view is still "correct except for ancestor tags". After the recursion, each partial node recomputes its sum
from its two children, which have just been made correct.

The cost is the same as a query: every operation visits $O(\log n)$ nodes, and a push is $O(1)$. In the program, adding
10 to $[2, 7)$ on eight zeros puts tags on just three nodes, $[2,4)$, $[4,6)$ and $[6,7)$; after the two sums, the tag on $[4,6)$ has
been pushed to its children, which is why the printed tags sit on nodes 5, 12, 13 and 14.

Lazy propagation works for any update that can be **composed** (two pending updates combine into one tag) and that
acts on the stored summary without looking at the elements (adding $x$ to a range adds $x \cdot$ length to its sum).
Examples are range assign with range sum, range add with range min, and "flip all bits in a range" with "count the 1s".

```python
--8<-- "books/algorithms/ch10_segment_tree.py"
```

```
a = [5, 8, 6, 3, 2, 7, 2, 6]
tree nodes 1..15: [2, 3, 2, 5, 3, 2, 2, 5, 8, 6, 3, 2, 7, 2, 6]
min a[1:6] = 2  nodes visited: 9
after a[4] = 9: min a[1:6] = 3  root = 2
after adding 10 to a[2:7]: sum a[0:8] = 50  sum a[5:8] = 20  pending adds: [0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 10, 10, 10, 0]
n = 50000: 3000 random operations agree with brute force: True; most nodes visited by one min query: 59 (4 log2 n is about 62)
```

**History.** Jon Bentley introduced segment trees in 1977 for a geometry problem, computing the area covered by a set
of rectangles; the array-based version with lazy tags became standard in programming contests much later. The
[segment tree reference page](../../data-structures/segment-tree.md) has a short version in three languages.

## 10.6 Sparse tables for range minimum; RMQ and LCA

*Level: intermediate; the RMQ-LCA part is advanced.*

If the array **never changes** and the operation is minimum (or maximum, gcd, bitwise AND or OR), we can answer every
query in $O(1)$ after $O(n\log n)$ preprocessing. This is the **range minimum query** (RMQ) problem.

**Sparse table.** For every $k$ with $2^k \le n$ and every start $i$, store $m_k[i] = \min(a_i, \dots, a_{i + 2^k - 1})$,
the minimum of the block of length $2^k$ starting at $i$. Row 0 is the array; each next row comes from the previous by

$$
m_{k}[i] = \min\big(m_{k-1}[i],\; m_{k-1}[i + 2^{k-1}]\big),
$$

because a block of length $2^k$ is two blocks of length $2^{k-1}$ side by side. There are $\lfloor\log_2 n\rfloor + 1$
rows of at most $n$ entries: $O(n\log n)$ time and space.

**Query** $[l, r)$: let $k = \lfloor\log_2(r - l)\rfloor$, the largest power of two that fits. Then the block of length
$2^k$ starting at $l$ and the block of length $2^k$ ending at $r$ (starting at $r - 2^k$) together cover $[l, r)$, since
$2^k + 2^k \ge r - l$; and both lie inside it. So

$$
\min(a_l, \dots, a_{r-1}) = \min\big(m_k[l],\; m_k[r - 2^k]\big) .
$$

The two blocks overlap, and elements in the overlap are counted twice, which does not change a minimum. That is why
this works for **idempotent** operations ($x \oplus x = x$) and not for sums. In Python, $k$ is `(r - l).bit_length() - 1`.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 720 176" role="img" aria-label="An array of 8 values. Two overlapping blocks of length 4 are drawn under positions 1 to 4 and 3 to 6; together they cover the query range 1 to 6.">
<rect x="80" y="30" width="70" height="30" rx="0" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="115.0" y="51" font-size="14" text-anchor="middle" fill="currentColor">5</text>
<text x="115.0" y="22" font-size="11" text-anchor="middle" fill="currentColor">0</text>
<rect x="150" y="30" width="70" height="30" rx="0" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="185.0" y="51" font-size="14" text-anchor="middle" fill="currentColor">8</text>
<text x="185.0" y="22" font-size="11" text-anchor="middle" fill="currentColor">1</text>
<rect x="220" y="30" width="70" height="30" rx="0" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="255.0" y="51" font-size="14" text-anchor="middle" fill="currentColor">6</text>
<text x="255.0" y="22" font-size="11" text-anchor="middle" fill="currentColor">2</text>
<rect x="290" y="30" width="70" height="30" rx="0" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="325.0" y="51" font-size="14" text-anchor="middle" fill="currentColor">3</text>
<text x="325.0" y="22" font-size="11" text-anchor="middle" fill="currentColor">3</text>
<rect x="360" y="30" width="70" height="30" rx="0" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="395.0" y="51" font-size="14" text-anchor="middle" fill="currentColor">2</text>
<text x="395.0" y="22" font-size="11" text-anchor="middle" fill="currentColor">4</text>
<rect x="430" y="30" width="70" height="30" rx="0" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="465.0" y="51" font-size="14" text-anchor="middle" fill="currentColor">7</text>
<text x="465.0" y="22" font-size="11" text-anchor="middle" fill="currentColor">5</text>
<rect x="500" y="30" width="70" height="30" rx="0" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="535.0" y="51" font-size="14" text-anchor="middle" fill="currentColor">2</text>
<text x="535.0" y="22" font-size="11" text-anchor="middle" fill="currentColor">6</text>
<rect x="570" y="30" width="70" height="30" rx="0" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="605.0" y="51" font-size="14" text-anchor="middle" fill="currentColor">6</text>
<text x="605.0" y="22" font-size="11" text-anchor="middle" fill="currentColor">7</text>
<rect x="152" y="75" width="276" height="24" rx="4" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/>
<text x="290" y="92" font-size="12" text-anchor="middle" fill="currentColor">m[2][1] = min a[1:5] = 2</text>
<rect x="292" y="108" width="276" height="24" rx="4" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<text x="430" y="125" font-size="12" text-anchor="middle" fill="currentColor">m[2][3] = min a[3:7] = 2</text>
<text x="360" y="160" font-size="12" text-anchor="middle" fill="currentColor">query a[1:7]: length 6, so k = 2 (blocks of 4); the overlap is harmless for min</text>
</svg>
<figcaption>Figure 10.4. A sparse-table query. Any range is the union of two blocks whose length is a power of two, one starting at the left end and one ending at the right end. Taking the minimum twice does not matter, so the answer is the smaller of two stored values: O(1).</figcaption>
</figure>

For $a = [5, 8, 6, 3, 2, 7, 2, 6]$ and the query $[1, 7)$: the length is 6, $k = 2$, and the answer is
$\min(m_2[1], m_2[3]) = \min(2, 2) = 2$.

### Lowest common ancestors

In a rooted tree, the **lowest common ancestor** LCA($u$, $v$) of two nodes is the deepest node that is an ancestor
of both (a node counts as its own ancestor). It answers questions like "how far apart are $u$ and $v$ in the tree?"
(depth($u$) + depth($v$) $-$ 2 depth(LCA)), and it appears in phylogenetic trees, file systems, version control
(the merge base of two branches) and string algorithms ([Chapter 18](18-String-Algorithms.md), on suffix trees).

**The reduction to RMQ.** Walk the tree depth-first and write down a node every time the walk **arrives** at it, both
on the way down and each time it comes back up from a child. This **Euler tour** has $2n - 1$ entries (one for the
root, plus two per edge: one going down and one coming back). Record the depth of each entry and the position
first($v$) of the first entry for each node $v$.

**Theorem 10.4.** If first($u$) $\le$ first($v$), then LCA($u$, $v$) is the entry of smallest depth in the Euler tour
between positions first($u$) and first($v$).

*Proof.* Let $w$ = LCA($u$, $v$). If $w = u$, then $v$ is in $u$'s subtree, and between the first visit of $u$ and the
first visit of $v$ the walk stays inside $u$'s subtree, where every node is deeper than $u$ except $u$ itself, which is
at the left end. Otherwise $u$ and $v$ are in the subtrees of two different children $c_1$ (visited first) and $c_2$ of
$w$. Between first($u$) and first($v$) the walk finishes $c_1$'s subtree, **returns to $w$** (an entry of depth
depth($w$)), and goes down into $c_2$'s subtree, possibly through other children of $w$ in between; it never leaves
$w$'s subtree, because it has not finished $w$. So every entry in the range has depth at least depth($w$), and $w$
itself appears. $\square$

The program builds the tour of a small tree, `A B D B E G E H E B A C F C A`, and answers LCA(G, D) = B,
LCA(H, F) = A, LCA(G, H) = E and LCA(E, G) = E with a sparse table over (depth, node) pairs: $O(n\log n)$
preprocessing, $O(1)$ per query.

```python
--8<-- "books/algorithms/ch10_sparse_table_lca.py"
```

```
k = 0 (blocks of 1): [5, 8, 6, 3, 2, 7, 2, 6]
k = 1 (blocks of 2): [5, 6, 3, 2, 2, 2, 2]
k = 2 (blocks of 4): [3, 2, 2, 2, 2]
k = 3 (blocks of 8): [2]
min a[1:7] = min(m[2][1], m[2][3]) = 2
Euler tour: A B D B E G E H E B A C F C A
depths    : 0 1 2 1 2 3 2 3 2 1 0 1 2 1 0
LCA(G, D) = B
LCA(H, F) = A
LCA(G, H) = E
LCA(E, G) = E
n = 100000: table has 17 rows, 1568946 entries; 2000 queries agree: True
```

### The other direction, and the optimal bounds

The reduction runs both ways. The **Cartesian tree** of an array (Vuillemin 1980) has the minimum at the root, the
Cartesian tree of the part to its left as the left subtree, and that of the part to its right as the right subtree; it
can be built in $O(n)$ with a stack. The minimum of $a[l..r]$ is the LCA of the nodes for $l$ and $r$. So RMQ and LCA
are the same problem up to linear-time conversions (Gabow, Bentley and Tarjan 1984).

Can we have $O(n)$ preprocessing **and** $O(1)$ queries? Yes. Harel and Tarjan (1984) gave the first such LCA
algorithm, which was complicated. Bender and Farach-Colton ("The LCA problem revisited", 2000) gave a simple one. The
Euler tour has a special property: adjacent depths differ by exactly $\pm1$. Cut the tour into blocks of
$\frac12\log_2 n$ entries; build a sparse table over the block minimums ($O(\frac{n}{\log n}\log n) = O(n)$); and
notice that a block is determined, up to an added constant, by its pattern of $+1$ and $-1$ steps, of which there are
only $2^{\frac12\log_2 n} = \sqrt n$ kinds, so all in-block answers for all kinds fit in a table of $O(\sqrt n\log^2 n)$
entries. A query combines at most two in-block lookups and one sparse-table lookup. Fischer and Heun (2011) later
showed how to do RMQ in $O(1)$ time with only about $2n$ bits beyond the array.

A simpler alternative for LCA is **binary lifting**: store each node's $2^k$-th ancestor for every $k$
($O(n\log n)$ space), and answer a query in $O(\log n)$ by lifting the deeper node to the same depth and then both nodes
together by decreasing powers of two. It also answers "what is the $k$-th ancestor of $v$?".

### Which range structure to use

| Data changes? | Operation | Structure | Build | Query | Update |
| --- | --- | --- | --- | --- | --- |
| no | sum (invertible) | prefix sums | $O(n)$ | $O(1)$ | $O(n)$ |
| no | min, max, gcd (idempotent) | sparse table | $O(n\log n)$ | $O(1)$ | rebuild |
| yes, points | sum (invertible) | Fenwick tree | $O(n)$ | $O(\log n)$ | $O(\log n)$ |
| yes, points or ranges | any associative | segment tree (lazy for ranges) | $O(n)$ | $O(\log n)$ | $O(\log n)$ |
| only range adds, read at the end | sum | difference array | $O(n)$ | at the end | $O(1)$ |

## Check yourself

??? question "1. Run plain quick-union (no ranks, no compression; union(a, b) sets parent[root(b)] = root(a)) on six objects with union(0,1), union(1,2), union(3,4), union(2,4), union(5,0). What is the parent array, and how many steps does find(4) take?"

    union(0,1): parent[1] = 0. union(1,2): root(1) = 0, so parent[2] = 0. union(3,4): parent[4] = 3. union(2,4):
    roots 0 and 3, parent[3] = 0. union(5,0): roots 5 and 0, parent[0] = 5. The array is [5, 0, 0, 0, 3, 5]. find(4)
    goes 4 → 3 → 0 → 5: three steps. One set holds all six objects.

??? question "2. Prove that with union by size (hang the tree with fewer nodes under the other), every node has depth at most log₂ n."

    A node's depth increases by 1 only when its tree is hung under another tree that is at least as large. Then the
    size of the tree containing it at least doubles. Sizes start at 1 and can never exceed $n$, so this happens at
    most $\log_2 n$ times.

??? question "3. Why does path compression not need to update ranks, and why is rank then no longer the height?"

    Compression only moves nodes closer to the root, so heights can only go down; the old rank is still an upper bound
    on the height, which is all the analysis needs (properties 1 to 3 in 10.2 remain true). Recomputing true heights
    after a compression would cost time and gain nothing, so ranks are left as they are, and a root's rank can be
    larger than its tree's current height.

??? question "4. Write the code: count the islands (groups of '#' cells joined by sides) in a grid with union-find."

    Give cell $(r, c)$ the number $rC + c$. Count land cells, and subtract one for every union that really merges
    two sets (each merge joins two islands into one).

    ```python
    def islands(grid):
        R, C = len(grid), len(grid[0])
        uf = UnionFind(R * C)
        land = 0
        for r in range(R):
            for c in range(C):
                if grid[r][c] == "#":
                    land += 1
                    for dr, dc in ((0, 1), (1, 0)):     # right and down neighbours
                        rr, cc = r + dr, c + dc
                        if rr < R and cc < C and grid[rr][cc] == "#":
                            if uf.union(r * C + c, rr * C + cc):
                                land -= 1
        return land

    print(islands(["##..#",
                   "#..##",
                   "..#..",
                   "##..#"]))      # 5
    ```

    `UnionFind` is the class from `ch10_union_find.py`, whose `union` returns True when it merges. Each cell is
    handled in $O(\alpha(n))$ amortized.

??? question "5. Write the code: Kruskal's minimum spanning tree, given union-find. Run it on the road map of Chapter 9 (Figure 9.5)."

    Sort the edges by weight and keep each edge whose ends are not yet connected:

    ```python
    def kruskal(n, edges):                 # edges as (weight, u, v)
        uf, tree = UnionFind(n), []
        for w, u, v in sorted(edges):
            if uf.union(u, v):
                tree.append((u, v, w))
        return tree

    edges = [(7, 0, 1), (9, 0, 2), (14, 0, 5), (10, 1, 2), (15, 1, 3),
             (11, 2, 3), (2, 2, 5), (6, 3, 4), (9, 4, 5)]
    t = kruskal(6, edges)
    print(t, sum(w for _, _, w in t))
    # [(2, 5, 2), (3, 4, 6), (0, 1, 7), (0, 2, 9), (4, 5, 9)] 33
    ```

    The sort costs $O(m\log m)$ and the unions $O(m\,\alpha(n))$. Why the kept edges form a minimum spanning tree is
    proved in [Chapter 17](17-Spanning-Trees-Flows-and-Matching.md) (the cut property).

??? question "6. On six zeros apply: add 2 to [0, 3), add 1 to [1, 6), add −3 to [2, 4). Use a difference array."

    $d_0 \mathrel{+}= 2$, $d_3 \mathrel{-}= 2$; $d_1 \mathrel{+}= 1$, ($d_6$ is past the end); $d_2 \mathrel{-}= 3$,
    $d_4 \mathrel{+}= 3$. So $d = [2, 1, -3, -2, 3, 0]$, and the prefix sums are $[2, 3, 0, -2, 1, 1]$.

??? question "7. In a Fenwick tree with n = 16, which entries does prefix(13) read, and which does add(5, v) write?"

    $13 = 1101_2$: read $t_{13}$, then clear the lowest bit to get $12 = 1100_2$, then $8 = 1000_2$, then 0. So
    $t_{13} + t_{12} + t_8$, covering $[13, 13]$, $[9, 12]$ and $[1, 8]$.

    $5 = 0101_2$: write $t_5$, then $5 + 1 = 6 = 0110_2$, then $6 + 2 = 8$, then $8 + 8 = 16$. So $t_5, t_6, t_8, t_{16}$.

??? question "8. A segment tree is built over n = 8 values as in Figure 10.3. How many nodes does it have? Why do implementations allocate 4n array slots for general n?"

    $2n - 1 = 15$: 8 leaves and 7 internal nodes (each internal node has two children, so there is one fewer internal
    node than leaves). With the heap numbering, when $n$ is a power of two the largest index is $2n - 1$. Otherwise the
    tree's leaves sit on two levels and the deepest level's indices can reach nearly $4n$ (the height is
    $\lceil\log_2 n\rceil$, so indices reach up to $2^{\lceil\log_2 n\rceil+1} - 1 < 4n$). Allocating $4n$ is a safe,
    simple bound.

??? question "9. Write the code: range add and range sum with two Fenwick trees."

    If every $a_i$ starts at 0 and we add $x$ to $[l, r]$, then the prefix sum up to $i$ grows by $x(i - l + 1)$ for
    $l \le i \le r$ and by $x(r - l + 1)$ for $i > r$. Both are of the form $i \cdot B_1(i) - B_2(i)$ if we add $x$ to
    $B_1$ at $l$ and $-x$ at $r + 1$, and $x(l - 1)$ to $B_2$ at $l$ and $-xr$ at $r + 1$, where $B_1(i)$ and $B_2(i)$
    are prefix sums of two Fenwick trees.

    ```python
    class RangeFenwick:                # Fenwick is the class from ch10_prefix_fenwick.py
        def __init__(self, n):
            self.b1, self.b2 = Fenwick(n), Fenwick(n)
        def add(self, l, r, x):        # a[l..r] += x, 1-based, inclusive
            self.b1.add(l, x)
            self.b2.add(l, x * (l - 1))
            if r + 1 <= self.b1.n:
                self.b1.add(r + 1, -x)
                self.b2.add(r + 1, -x * r)
        def prefix(self, i):
            return self.b1.prefix(i) * i - self.b2.prefix(i)
        def range_sum(self, l, r):
            return self.prefix(r) - self.prefix(l - 1)
    ```

    Checked against a plain list on 2000 random operations. Check the formula at $l \le i \le r$:
    $xi - x(l - 1) = x(i - l + 1)$; at $i > r$: $(x - x)i - (x(l-1) - xr) = x(r - l + 1)$.

??? question "10. Why can a sparse table answer range minimum but not range sum in O(1)? How much memory does it need for n = 10⁶?"

    The query covers $[l, r)$ with two blocks that overlap. For min, counting an element twice changes nothing
    ($\min(x, x) = x$); for sum it would add the overlap twice, and there is no cheap way to know which elements are in
    it without subtracting, which a sum table would need prefix sums for anyway. For $n = 10^6$ there are
    $\lfloor\log_2 10^6\rfloor + 1 = 20$ rows; row $k$ has $n - 2^k + 1$ entries, about 18.95 million in all, so about
    19 times the size of the array.

??? question "11. In the program's tree (A has children B, C; B has D, E; C has F; E has G, H), find LCA(D, H) and LCA(F, C) from the Euler tour by hand."

    Tour `A B D B E G E H E B A C F C A` with depths `0 1 2 1 2 3 2 3 2 1 0 1 2 1 0`. first(D) = 2, first(H) = 7: the
    entries at positions 2 to 7 are D B E G E H with depths 2 1 2 3 2 3; the smallest depth is at B. So LCA(D, H) = B.
    first(C) = 11, first(F) = 12: entries C F, the smallest depth is C. So LCA(F, C) = C, as it should be, since C is
    F's parent.

??? question "12. Write the code: count the inversions of a list (pairs i < j with a[i] > a[j]) in O(n log n) with a Fenwick tree."

    Go left to right. Keep a Fenwick tree counting how many of the earlier keys have each rank. When key $x$ arrives
    after `seen` keys, the earlier keys greater than $x$ are `seen` minus the number at most $x$.

    ```python
    def inversions(a):
        ranks = {v: i + 1 for i, v in enumerate(sorted(set(a)))}
        f, inv = Fenwick(len(ranks)), 0
        for seen, x in enumerate(a):
            inv += seen - f.prefix(ranks[x])   # earlier keys greater than x
            f.add(ranks[x], 1)
        return inv

    print(inversions([3, 1, 4, 1, 5, 9, 2, 6]))   # 8
    ```

    A brute-force count over all pairs also gives 8. [Chapter 11](11-Divide-and-Conquer.md) counts inversions a
    second way, by merge sort.

## What you learned

- Union-find keeps disjoint sets as trees of parent pointers; union by rank keeps every rank, and so every height,
  at most $\log_2 n$, with at most $n/2^r$ nodes of rank $r$.
- Adding path compression makes $m$ operations cost $O(m\log^* n)$ (proved by grouping ranks into tower blocks), and
  in fact $O(m\,\alpha(m, n))$, which is optimal; $\alpha$ never exceeds 4 in practice.
- Prefix sums answer static range sums in $O(1)$ after $O(n)$ work; difference arrays apply many range adds in $O(1)$
  each; both extend to two dimensions by inclusion-exclusion.
- A Fenwick tree stores sums of blocks whose length is the lowest 1-bit of the index (`i & -i`, from two's
  complement); prefix sums and point updates each take one step per bit, $O(\log n)$.
- A segment tree handles any associative operation in $O(\log n)$ per query (at most four nodes per level), and lazy
  tags extend it to range updates.
- A sparse table answers idempotent range queries like minimum in $O(1)$ by two overlapping power-of-two blocks; the
  Euler tour turns lowest common ancestors into range minimum, and the two problems are equivalent.

**Next:** [Chapter 11](11-Divide-and-Conquer.md), divide and conquer: the design technique behind merge sort, fast
multiplication and the fast Fourier transform.

## Further reading

- T. H. Cormen, C. E. Leiserson, R. L. Rivest and C. Stein, *Introduction to Algorithms*, 4th ed., 2022: chapter 19
  (data structures for disjoint sets, with the full inverse-Ackermann proof).
- R. Sedgewick and K. Wayne, *Algorithms*, 4th ed., 2011: section 1.5 (union-find, developed from quick-find to
  weighted quick-union with path compression).
- J. Kleinberg and É. Tardos, *Algorithm Design*, 2005: section 4.6 (union-find for Kruskal's algorithm).
- B. A. Galler and M. J. Fischer, "An improved equivalence algorithm", *Communications of the ACM*, 1964.
- J. E. Hopcroft and J. D. Ullman, "Set merging algorithms", *SIAM Journal on Computing*, 1973.
- R. E. Tarjan, "Efficiency of a good but not linear set union algorithm", *Journal of the ACM*, 1975; and R. E.
  Tarjan and J. van Leeuwen, "Worst-case analysis of set union algorithms", *Journal of the ACM*, 1984.
- M. L. Fredman and M. E. Saks, "The cell probe complexity of dynamic data structures", STOC 1989.
- P. M. Fenwick, "A new data structure for cumulative frequency tables", *Software: Practice and Experience*, 1994.
- M. A. Bender and M. Farach-Colton, "The LCA problem revisited", LATIN 2000.
- D. Harel and R. E. Tarjan, "Fast algorithms for finding nearest common ancestors", *SIAM Journal on Computing*, 1984.
- J. Fischer and V. Heun, "Space-efficient preprocessing schemes for range minimum queries on static arrays", *SIAM
  Journal on Computing*, 2011.
- On this site: the reference pages [union-find](../../data-structures/union-find.md),
  [Fenwick tree](../../data-structures/fenwick-tree.md), [segment tree](../../data-structures/segment-tree.md) and
  [Kruskal's algorithm](../../graphs/kruskal.md); [Chapter 9](09-Heaps-and-Priority-Queues.md) for the array layout of
  complete trees; [Chapter 17](17-Spanning-Trees-Flows-and-Matching.md) for union-find inside Kruskal's algorithm.
