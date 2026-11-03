# 8. Trees and balanced search trees

*A sorted array answers "is this key here?" in $O(\log n)$ steps by binary search, but inserting one new key costs
$O(n)$ because everything after it must move. A hash table inserts in $O(1)$ but forgets the order, so it cannot
answer "what is the next key after 42?" or "list every key between 100 and 200". This chapter builds the structure
that does all of these in $O(\log n)$: the balanced search tree. You will start with the words for trees and the four
ways to walk one, build a plain binary search tree and watch it collapse into a list, and then fix it four different
ways: by height rules (AVL), by colour rules (red-black), by fat nodes for disks (B-trees), and by coin flips (treaps
and skip lists). Last comes the splay tree, which has no rule at all and still wins on average.*

!!! abstract "In this chapter"
    **You will learn:**

    - the words for trees (root, leaf, parent, child, depth, height, subtree) and the pre-, in-, post- and level-order walks
    - how a binary search tree searches, inserts and deletes, why each is correct, and why all three cost $O(h)$ for height $h$
    - how rotations rebalance a tree, and why an AVL tree's height is at most about $1.44 \log_2 n$ (a Fibonacci argument)
    - the five red-black rules, the proof that they keep the height below $2\log_2(n+1)$, and the three insertion cases
    - why databases and file systems use B-trees with hundreds of keys per node
    - how treaps and skip lists get expected $O(\log n)$ from randomness, with proofs
    - how splay trees adjust themselves to the pattern of accesses

    **You need:** [Chapter 3](03-Recursion-and-Induction.md) (induction, recursion), [Chapter 4](04-Lists-Stacks-and-Queues.md)
    (linked structures, queues, amortized cost), [Chapter 7](07-Searching-and-Hashing.md) (binary search, dictionaries).
    The Fibonacci numbers appear in 8.3; [Chapter 13](13-Dynamic-Programming.md) is not needed for that.

    **Levels:** 8.1 and 8.2 are beginner; 8.3 to 8.5 are intermediate; 8.6 and 8.7 are advanced.

## 8.1 Trees: the words and the four walks

How would you store a family tree, the folders on a disk, or the chapters and sections of this book? None of them is
a line of items; each item has *one* item above it and *any number* below it. That shape is a **tree**.

A **rooted tree** is a set of **nodes** joined by **edges** such that one node, the **root**, has nothing above it,
every other node has exactly one node directly above it, its **parent**, and following parents from any node always
reaches the root. The nodes directly below a node are its **children**. A node with no children is a **leaf**; the
others are **internal** nodes. The **subtree** of a node $x$ is $x$ together with everything below it.

Two measurements matter all chapter long:

- the **depth** of a node is the number of edges from the root down to it; the root has depth 0;
- the **height** of a tree is the largest depth of any node. A one-node tree has height 0, and we say the empty tree
  has height $-1$, so that "height of a node = 1 + the larger height of its two subtrees" works everywhere.

A **binary tree** is a rooted tree in which every node has at most two children, called **left** and **right**. The
order matters: a node with only a left child is a different tree from a node with only a right child.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 720 290" role="img" aria-label="A binary search tree with root 8. Depth 1: 3 and 10. Depth 2: 1, 6 and 14. Depth 3: 4, 7 and 13. The root is orange, the leaves 1, 4, 7 and 13 are green, and the subtree of 6 is boxed.">
<line x1="70" y1="40" x2="600" y2="40" stroke="currentColor" stroke-width="0.6" stroke-dasharray="5 4" opacity="0.45"/>
<text x="10" y="45" font-size="12" text-anchor="start" fill="currentColor">depth 0</text>
<line x1="70" y1="100" x2="600" y2="100" stroke="currentColor" stroke-width="0.6" stroke-dasharray="5 4" opacity="0.45"/>
<text x="10" y="105" font-size="12" text-anchor="start" fill="currentColor">depth 1</text>
<line x1="70" y1="160" x2="600" y2="160" stroke="currentColor" stroke-width="0.6" stroke-dasharray="5 4" opacity="0.45"/>
<text x="10" y="165" font-size="12" text-anchor="start" fill="currentColor">depth 2</text>
<line x1="70" y1="220" x2="600" y2="220" stroke="currentColor" stroke-width="0.6" stroke-dasharray="5 4" opacity="0.45"/>
<text x="10" y="225" font-size="12" text-anchor="start" fill="currentColor">depth 3</text>
<line x1="340" y1="40" x2="200" y2="100" stroke="currentColor" stroke-width="1.5"/>
<line x1="340" y1="40" x2="480" y2="100" stroke="currentColor" stroke-width="1.5"/>
<line x1="200" y1="100" x2="130" y2="160" stroke="currentColor" stroke-width="1.5"/>
<line x1="200" y1="100" x2="270" y2="160" stroke="currentColor" stroke-width="1.5"/>
<line x1="480" y1="100" x2="550" y2="160" stroke="currentColor" stroke-width="1.5"/>
<line x1="270" y1="160" x2="230" y2="220" stroke="currentColor" stroke-width="1.5"/>
<line x1="270" y1="160" x2="310" y2="220" stroke="currentColor" stroke-width="1.5"/>
<line x1="550" y1="160" x2="510" y2="220" stroke="currentColor" stroke-width="1.5"/>
<circle cx="340" cy="40" r="17" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/><text x="340" y="45" font-size="14" text-anchor="middle" fill="currentColor">8</text>
<circle cx="200" cy="100" r="17" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/><text x="200" y="105" font-size="14" text-anchor="middle" fill="currentColor">3</text>
<circle cx="480" cy="100" r="17" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/><text x="480" y="105" font-size="14" text-anchor="middle" fill="currentColor">10</text>
<circle cx="130" cy="160" r="17" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/><text x="130" y="165" font-size="14" text-anchor="middle" fill="currentColor">1</text>
<circle cx="270" cy="160" r="17" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/><text x="270" y="165" font-size="14" text-anchor="middle" fill="currentColor">6</text>
<circle cx="550" cy="160" r="17" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/><text x="550" y="165" font-size="14" text-anchor="middle" fill="currentColor">14</text>
<circle cx="230" cy="220" r="17" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/><text x="230" y="225" font-size="14" text-anchor="middle" fill="currentColor">4</text>
<circle cx="310" cy="220" r="17" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/><text x="310" y="225" font-size="14" text-anchor="middle" fill="currentColor">7</text>
<circle cx="510" cy="220" r="17" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/><text x="510" y="225" font-size="14" text-anchor="middle" fill="currentColor">13</text>
<text x="388" y="45" font-size="13" text-anchor="start" fill="currentColor">root</text>
<text x="130" y="196" font-size="12" text-anchor="middle" fill="currentColor">leaf</text>
<text x="292" y="132" font-size="12" text-anchor="middle" fill="currentColor">subtree of 6</text>
<rect x="205" y="140" width="130" height="102" rx="4" fill="none" stroke="currentColor" stroke-width="1.2" stroke-dasharray="5 4"/>
<rect x="70" y="262" width="14" height="14" rx="2" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/>
<text x="90" y="274" font-size="12" text-anchor="start" fill="currentColor">root</text>
<rect x="150" y="262" width="14" height="14" rx="2" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="170" y="274" font-size="12" text-anchor="start" fill="currentColor">internal node</text>
<rect x="290" y="262" width="14" height="14" rx="2" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<text x="310" y="274" font-size="12" text-anchor="start" fill="currentColor">leaf</text>
<text x="370" y="274" font-size="12" text-anchor="start" fill="currentColor">height = 3 (longest path, in edges)</text>
</svg>
<figcaption>Figure 8.1. The binary search tree built by inserting 8, 3, 10, 1, 6, 14, 4, 7, 13 in that order. Every key in a left subtree is smaller than its ancestor, every key in a right subtree larger. Depth is the number of edges from the root; the height is the largest depth.</figcaption>
</figure>

**How many nodes fit in a given height?** Depth 0 holds at most one node, and each node has at most two children, so
depth $d$ holds at most $2^d$ nodes. A binary tree of height $h$ therefore holds at most

$$
1 + 2 + 4 + \dots + 2^h = 2^{h+1} - 1
$$

nodes (the geometric sum of [Chapter 2](02-Measuring-Cost.md)). Turn it around: if a binary tree has $n$ nodes and
height $h$, then $n \le 2^{h+1}-1$, so

$$
h \ge \log_2(n+1) - 1 .
$$

No binary tree on a million nodes can have height below 19. This is the floor every balanced tree in this chapter
tries to stay near. The ceiling is just as easy: a tree of height $h$ needs at least $h+1$ nodes (one per depth), so
the worst height for $n$ nodes is $n-1$, a single path. The whole chapter is about staying near the floor.

### Four ways to walk a tree

To print, copy, check or free every node we must **traverse** the tree: visit each node exactly once. Three walks
come straight from recursion. Each one handles the left subtree, the right subtree and the node itself; they differ
only in when the node is visited.

| Walk | Order | Figure 8.1 gives |
| --- | --- | --- |
| **preorder** | node, then left subtree, then right subtree | 8, 3, 1, 6, 4, 7, 10, 14, 13 |
| **inorder** | left subtree, then node, then right subtree | 1, 3, 4, 6, 7, 8, 10, 13, 14 |
| **postorder** | left subtree, then right subtree, then node | 1, 4, 7, 6, 3, 13, 14, 10, 8 |
| **level order** | depth 0, then depth 1, ..., each from left to right | 8, 3, 10, 1, 6, 14, 4, 7, 13 |

Here is the inorder walk by hand on Figure 8.1, writing the call stack after each visit:

| Step | Calls waiting (innermost last) | Visited so far |
| --- | --- | --- |
| 1 | in(8), in(3), in(1) | 1 |
| 2 | in(8), in(3) | 1, 3 |
| 3 | in(8), in(3), in(6), in(4) | 1, 3, 4 |
| 4 | in(8), in(3), in(6) | 1, 3, 4, 6 |
| 5 | in(8), in(3), in(6), in(7) | 1, 3, 4, 6, 7 |
| 6 | in(8) | 1, 3, 4, 6, 7, 8 |
| 7 | in(8), in(10) | ..., 8, 10 |
| 8 | in(8), in(10), in(14), in(13) | ..., 10, 13 |
| 9 | in(8), in(10), in(14) | ..., 13, 14 |

The stack never holds more than $h+1$ calls, so the walk needs $O(h)$ extra memory, and it touches each node a
constant number of times, so it takes $O(n)$ time. The same holds for preorder and postorder.

**Why each walk exists.** Preorder lists a node before anything below it, the order in which you would *create* a
copy of the tree, or print a table of contents with indentation. Postorder lists a node after everything below it,
the order in which you can *delete* a tree, or add up the sizes of folders (a folder's size needs its children's
sizes first). Inorder, as we will prove in a moment, lists a binary search tree in sorted order.

The level-order walk is not recursive at all. It uses a **queue** ([Chapter 4](04-Lists-Stacks-and-Queues.md)): put
the root in; repeatedly take the front node out, visit it, and put its children in at the back. Nodes leave the
queue in order of depth, because every node at depth $d$ enters before any node at depth $d+1$ (each depth-$(d+1)$
node is put in when its depth-$d$ parent leaves). It is the same idea as breadth-first search on a graph, which
[Chapter 15](15-Graphs-and-Graph-Search.md) develops in full.

```python
from collections import deque

def level_order(t):
    out, q = [], deque([t] if t else [])
    while q:
        x = q.popleft()
        out.append(x.key)
        q.extend(c for c in (x.left, x.right) if c)
    return out
```

## 8.2 Binary search trees

A **binary search tree** (BST) is a binary tree with a key in every node and one rule, the **search-tree property**:

> for every node $x$, every key in $x$'s left subtree is smaller than $x$'s key, and every key in $x$'s right subtree
> is larger.

(We assume distinct keys. If equal keys must be stored, keep a count in the node, or a list of values.) Figure 8.1 is
a BST. The rule is about whole subtrees, not just children: in Figure 8.1, 7 sits in the left subtree of 8, so it must
be smaller than 8, and it is. A check that only compares each node with its two children is wrong; exercise 7 asks
you to break one.

**Theorem 8.1.** The inorder walk of a BST lists its keys in increasing order.

*Proof,* by strong induction on the number of nodes $n$. For $n = 0$ the walk lists nothing, which is sorted. For a
tree with root $r$, the walk lists the left subtree, then $r$, then the right subtree. By induction the left part is
sorted and the right part is sorted (each subtree is a smaller BST). Every key in the left part is below $r$'s key and
every key in the right part is above it, by the search-tree property. So the whole list is sorted. $\square$

That theorem is the reason a BST is useful: it is a sorted list that you can also cut into halves at every node.

### Search

To look for key $k$, start at the root. If the node's key is $k$, stop. If $k$ is smaller, the left subtree is the
only place it can be; if larger, the right subtree. Keep going until you find it or fall off the tree.

**Why it is correct.** The loop keeps this **invariant**: *if $k$ is anywhere in the tree, it is in the subtree of the
current node.* At the start the current node is the root, so it holds. If $k$ is smaller than the current key, the
search-tree property says $k$ is not in the right subtree and not the current node, so if it is in the current
subtree at all it is in the left one: moving left keeps the invariant. The same goes for right. When the current
subtree is empty, the invariant says $k$ is not in the tree. Each step goes one level deeper, so the search stops
after at most $h+1$ nodes: the cost is $O(h)$.

The same walk answers the questions a hash table cannot. The **minimum** is found by going left until you cannot;
the maximum by going right. The **successor** of $x$ (the next larger key) is the minimum of $x$'s right subtree if
it has one; otherwise it is the nearest ancestor of which $x$ lies in the *left* subtree. A **range query** "all keys
between $a$ and $b$" is an inorder walk that skips any subtree lying wholly outside $[a, b]$; it costs $O(h + r)$ for
$r$ answers.

### Insert

Search for the new key. If you find it, there is nothing to do. Otherwise the search falls off the tree at an empty
child slot: hang a new leaf there. The new leaf is in the one place the search for it will look, and no existing key
changes place, so the search-tree property still holds for every old node (the new key is on the correct side of
every ancestor, because the search went left exactly where it was smaller). Cost: $O(h)$.

### Delete

Deleting node $z$ has three cases.

1. $z$ is a **leaf**: remove it.
2. $z$ has **one child**: let the child take $z$'s place (splice $z$ out). Everything in the child's subtree was on the
   same side of every ancestor of $z$ as $z$ was, so the order is kept.
3. $z$ has **two children**: find $z$'s **successor** $s$, the minimum of the right subtree. Copy $s$'s key into $z$,
   then delete $s$ from the right subtree. Because $s$ is a minimum, it has no left child, so that second deletion is
   case 1 or 2.

**Why case 3 keeps the order.** The successor $s$ is larger than every key in $z$'s left subtree (it is larger than
$z$) and smaller than every other key in the right subtree (it is their minimum). So in $z$'s position it separates
the two subtrees correctly, and it stays on the right side of every ancestor because $z$ was. Cost: finding $s$ and
splicing it out walk one path, so $O(h)$.

The program below builds Figure 8.1, walks it four ways, and deletes a leaf (4), a node with one child (10) and a
node with two children (3). The trees are printed as `key(left,right)` with `.` for an empty child.

```python
--8<-- "books/algorithms/ch08_bst.py"
```

```
tree      : 8(3(1,6(4,7)),10(.,14(13,.)))
preorder  : [8, 3, 1, 6, 4, 7, 10, 14, 13]
inorder   : [1, 3, 4, 6, 7, 8, 10, 13, 14]
postorder : [1, 4, 7, 6, 3, 13, 14, 10, 8]
level     : [8, 3, 10, 1, 6, 14, 4, 7, 13]
height    : 3
search 7  : True | search 5: False
delete  4 : 8(3(1,6(.,7)),10(.,14(13,.))) | still a BST: True
delete 10 : 8(3(1,6(.,7)),14(13,.)) | still a BST: True
delete  3 : 8(6(1,7),14(13,.)) | still a BST: True
n = 1000: height after sorted inserts = 999, after random inserts = 21
```

Look at the last line. The first version of this program used the recursive `insert` for the 1000 sorted keys, and
Python stopped with `RecursionError: maximum recursion depth exceeded`: the tree was a path 1000 nodes deep, and a
recursive insert needs one stack frame per level ([Chapter 3](03-Recursion-and-Induction.md) explains Python's limit
of about 1000 frames). That is why the file has a loop version, `insert_loop`.

### Why a plain BST can degrade

Everything costs $O(h)$, but $h$ depends on the **order** of insertions. Insert $1, 2, 3, \dots, n$ in increasing
order: each key is larger than all before it, so it goes to the right of every node, and the tree is a path of height
$n-1$. Searching it is a linear search. Sorted input is not a rare accident; it is what you get from reading a sorted
file, numbering records, or inserting timestamps.

In a **random** order the tree is shallow. If all $n!$ orders are equally likely, the average depth of a node is about
$2\ln n \approx 1.39\log_2 n$. The proof is the same counting as for randomized quicksort in
[Chapter 5](05-Sorting-by-Comparison.md): the first key inserted becomes the root and splits the others exactly like a
quicksort pivot, and key $i$ ends up an ancestor of key $j$ exactly when $i$ is inserted first among all the keys
between them. We prove exactly that statement for treaps in 8.6. The expected *height* is also $O(\log n)$; Devroye
(1986) showed it is about $4.311\ln n$ for large $n$. In the program, 1000 random keys gave height 21 against 999 for
sorted keys.

But we cannot choose the order in which users hand us keys. The rest of the chapter makes the height $O(\log n)$
whatever the order: either by **rules** that are restored after every change (8.3 to 8.5) or by **randomness** that
we control ourselves (8.6).

The [binary search tree reference page](../../data-structures/bst.md) has the same operations in Python, Java and C++
with an animation.

## 8.3 AVL trees

*Level: intermediate.*

Can we keep a BST balanced with a rule that is cheap to check locally? Georgy Adelson-Velsky and Evgenii Landis, at
Moscow, gave the first answer in a 1962 paper, "An algorithm for the organization of information". Their trees are
called **AVL trees**.

**The AVL rule.** For every node, the heights of its left and right subtrees differ by at most 1.

The **balance factor** of a node is height(left) $-$ height(right); the rule says it is $-1$, $0$ or $+1$. Each node
stores its own height, so the balance factor is two lookups and a subtraction.

### Rotations

When an insertion breaks the rule somewhere, we repair it with a **rotation**, the basic move of every balanced tree
in this chapter. A **right rotation** at $y$ takes $y$'s left child $x$ and makes it the parent of $y$; $x$'s old right
subtree $B$ moves across to become $y$'s left subtree. A **left rotation** is the mirror image.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 680 280" role="img" aria-label="Left: y at the top with left child x; x has subtrees A and B, y has right subtree C. Right: x at the top with left subtree A and right child y; y has subtrees B and C. Arrows: rotate right turns the left tree into the right one, rotate left turns it back.">
<line x1="150" y1="50" x2="90" y2="120" stroke="currentColor" stroke-width="1.5"/>
<line x1="150" y1="50" x2="220" y2="130" stroke="currentColor" stroke-width="1.5"/>
<line x1="90" y1="120" x2="50" y2="180" stroke="currentColor" stroke-width="1.5"/>
<line x1="90" y1="120" x2="130" y2="180" stroke="currentColor" stroke-width="1.5"/>
<polygon points="220,130 190.0,190 250.0,190" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/><text x="220" y="182" font-size="14" text-anchor="middle" fill="currentColor">C</text>
<polygon points="50,180 22.0,236 78.0,236" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/><text x="50" y="228" font-size="14" text-anchor="middle" fill="currentColor">A</text>
<polygon points="130,180 102.0,236 158.0,236" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/><text x="130" y="228" font-size="14" text-anchor="middle" fill="currentColor">B</text>
<circle cx="150" cy="50" r="17" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/><text x="150" y="55" font-size="14" text-anchor="middle" fill="currentColor">y</text>
<circle cx="90" cy="120" r="17" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/><text x="90" y="125" font-size="14" text-anchor="middle" fill="currentColor">x</text>
<line x1="500" y1="50" x2="440" y2="130" stroke="currentColor" stroke-width="1.5"/>
<line x1="500" y1="50" x2="570" y2="120" stroke="currentColor" stroke-width="1.5"/>
<line x1="570" y1="120" x2="530" y2="180" stroke="currentColor" stroke-width="1.5"/>
<line x1="570" y1="120" x2="610" y2="180" stroke="currentColor" stroke-width="1.5"/>
<polygon points="440,130 410.0,190 470.0,190" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/><text x="440" y="182" font-size="14" text-anchor="middle" fill="currentColor">A</text>
<polygon points="530,180 502.0,236 558.0,236" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/><text x="530" y="228" font-size="14" text-anchor="middle" fill="currentColor">B</text>
<polygon points="610,180 582.0,236 638.0,236" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/><text x="610" y="228" font-size="14" text-anchor="middle" fill="currentColor">C</text>
<circle cx="500" cy="50" r="17" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/><text x="500" y="55" font-size="14" text-anchor="middle" fill="currentColor">x</text>
<circle cx="570" cy="120" r="17" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/><text x="570" y="125" font-size="14" text-anchor="middle" fill="currentColor">y</text>
<line x1="275" y1="95" x2="376.0" y2="95.0" stroke="currentColor" stroke-width="1.5"/><polygon points="385,95 376.0,99.0 376.0,91.0" fill="currentColor"/>
<line x1="385" y1="125" x2="284.0" y2="125.0" stroke="currentColor" stroke-width="1.5"/><polygon points="275,125 284.0,121.0 284.0,129.0" fill="currentColor"/>
<text x="330" y="86" font-size="12" text-anchor="middle" fill="currentColor">rotate right at y</text>
<text x="330" y="145" font-size="12" text-anchor="middle" fill="currentColor">rotate left at x</text>
<text x="330" y="262" font-size="13" text-anchor="middle" fill="currentColor">in-order in both: A, x, B, y, C</text>
</svg>
<figcaption>Figure 8.2. A rotation changes which of two nodes is the parent, moves one subtree (B) across, and keeps the in-order sequence A, x, B, y, C. Only three links change, so a rotation costs O(1).</figcaption>
</figure>

**A rotation keeps the search-tree property.** Before, the inorder sequence is $A, x, B, y, C$ (everything in $A$ is
below $x$, $B$ is between $x$ and $y$, $C$ is above $y$). After, it is $A, x, B, y, C$ again: $A$ is still left of $x$,
$B$ is right of $x$ and left of $y$, $C$ right of $y$. Keys outside the picture do not move relative to it. A rotation
changes three pointers and two stored heights, so it costs $O(1)$; what it changes is the *shape*: $A$ moves up one
level and $C$ moves down one level.

### Insertion

Insert as in a plain BST, then walk back up the path to the root, recomputing heights. The first node whose balance
factor becomes $\pm 2$, call it $z$, is repaired. There are four cases, named by the first two steps from $z$ towards
the new leaf:

| Case | New key went | Repair |
| --- | --- | --- |
| LL | left, then left | rotate right at $z$ |
| RR | right, then right | rotate left at $z$ |
| LR | left, then right | rotate left at $z$'s left child, then right at $z$ (a **double rotation**) |
| RL | right, then left | rotate right at $z$'s right child, then left at $z$ |

**Why one repair is enough.** Take the LL case. Say $z$'s right subtree has height $k$. Before the insertion $z$ was
balanced and its left child $x$ became too tall by one, so $x$'s subtree had height $k+1$ and now has $k+2$; the new
leaf went into $x$'s left subtree $A$, which now has height $k+1$, while $x$'s right subtree $B$ has height $k$ (if
$B$ were $k+1$ too, $x$'s height would not have grown). After rotating right at $z$: $z$ has children $B$ and the old
right subtree, both of height $k$, so $z$ has height $k+1$; $x$ has children $A$ (height $k+1$) and $z$ (height $k+1$),
so $x$ is balanced with height $k+2$. That is exactly the height $z$ had *before* the insertion. So every node above is
unaffected and the repair is complete: an AVL insertion needs **at most one** single or double rotation. The LR case
is the same calculation with the middle subtree split into its two halves; the double rotation brings the middle node
up and leaves both $x$ and $z$ with height $k+1$.

Here is the trace that the program below prints, for inserting 10, 20, 30, 25, 28, 5, 3:

| Insert | Tree after (`key(left,right)`) | Repair |
| --- | --- | --- |
| 10 | 10 | none |
| 20 | 10(.,20) | none: balance at 10 is $-1$ |
| 30 | 20(10,30) | RR at 10: balance was $-2$, rotate left |
| 25 | 20(10,30(25,.)) | none |
| 28 | 20(10,28(25,30)) | LR at 30: 28 went left (to 25) then right; double rotation brings 28 up |
| 5 | 20(10(5,.),28(25,30)) | none |
| 3 | 20(5(3,10),28(25,30)) | LL at 10: rotate right |

**Deletion** works the same way: delete as in a BST, walk up, and repair each node whose balance became $\pm2$. The
difference is that a repair after a deletion can leave the subtree one *shorter* than before, so the imbalance can
move up: a deletion may need a rotation at every level, $O(\log n)$ rotations, which is still $O(\log n)$ time.

### The height bound, proved via Fibonacci

**Theorem 8.2.** An AVL tree with $n$ nodes has height $h \le \log_\varphi(n+1) - 1 < 1.4405\log_2(n+1)$, where
$\varphi = (1+\sqrt5)/2 \approx 1.618$ is the golden ratio.

*Proof.* Turn the question around: what is the **fewest** nodes $N(h)$ an AVL tree of height $h$ can have? A height-0
tree is one node, $N(0) = 1$; a height-1 tree needs a root and a child, $N(1) = 2$. For $h \ge 2$, the root has one
subtree of height $h-1$ (otherwise the height would not be $h$) and, to use as few nodes as possible, the other subtree
as short as the rule allows: $h-2$. Both subtrees are themselves AVL trees and should be as small as possible, so

$$
N(h) = N(h-1) + N(h-2) + 1 .
$$

This looks like the Fibonacci recurrence $F(k) = F(k-1) + F(k-2)$ with $F(1) = F(2) = 1$, and indeed
$N(h) = F(h+3) - 1$. Check by induction: $N(0) = F(3) - 1 = 1$, $N(1) = F(4) - 1 = 2$, and if it holds for $h-1$ and
$h-2$ then $N(h) = (F(h+2) - 1) + (F(h+1) - 1) + 1 = F(h+3) - 1$.

Next, $F(k) \ge \varphi^{k-2}$ for every $k \ge 1$. It holds for $k = 1$ ($1 \ge \varphi^{-1} \approx 0.618$) and
$k = 2$ ($1 \ge 1$). The golden ratio satisfies $\varphi^2 = \varphi + 1$, so if it holds for $k-1$ and $k-2$,

$$
F(k) = F(k-1) + F(k-2) \ge \varphi^{k-3} + \varphi^{k-4} = \varphi^{k-4}(\varphi + 1) = \varphi^{k-4}\varphi^2 = \varphi^{k-2} .
$$

So an AVL tree of height $h$ with $n$ nodes has $n \ge N(h) = F(h+3) - 1 \ge \varphi^{h+1} - 1$. Take logarithms:
$h + 1 \le \log_\varphi(n+1)$. Finally $\log_\varphi x = \log_2 x / \log_2\varphi$ and $1/\log_2\varphi \approx 1.4404$.
$\square$

If you only want "$O(\log n)$" there is a two-line version: $N(h) > 2N(h-2)$, so $N(h) > 2^{h/2}$ and
$h < 2\log_2 n$. The Fibonacci version tells you the true constant: an AVL tree is never more than about 44 percent
taller than the best possible tree.

The trees that achieve $N(h)$ exactly are called **Fibonacci trees**; they are the most lopsided trees the AVL rule
allows. The program checks $N(h) = F(h+3)-1$ and then measures a big tree after 100,000 insertions and 50,000
deletions.

```python
--8<-- "books/algorithms/ch08_avl.py"
```

```
insert 10: 10                                 -
insert 20: 10(.,20)                           -
insert 30: 20(10,30)                          RR at 10
insert 25: 20(10,30(25,.))                    -
insert 28: 20(10,28(25,30))                   LR at 30
insert  5: 20(10(5,.),28(25,30))              -
insert  3: 20(5(3,10),28(25,30))              LL at 10
h  N(h)  F(h+3)-1
0     1     1
1     2     2
2     4     4
3     7     7
4    12    12
5    20    20
6    33    33
7    54    54
n = 50000: AVL height 18, log2(n) = 15.6, bound 1.44*log2(n+2) = 22.5
```

Height 18 for 50,000 keys: the best possible is 15, the theorem allows 21.5 (the program prints the slightly weaker
$1.44\log_2(n+2)$), and a plain BST built from the same keys in random order is typically around 36 (three seeds gave 35, 36 and 37).

## 8.4 Red-black trees

*Level: intermediate.*

AVL trees are tightly balanced, but they store a height in every node and deletions may rotate all the way up. A
looser rule, with one bit per node and $O(1)$ rotations for every insertion *and* deletion, turned out to be the
favourite of library writers. Rudolf Bayer described the idea in 1972 as "symmetric binary B-trees"; Leonidas Guibas
and Robert Sedgewick recast it with two colours in 1978 ("A dichromatic framework for balanced trees") and the name
**red-black tree** comes from them. Java's `TreeMap`, the usual implementations of C++'s `std::map` and `std::set`, and
the Linux kernel's `rbtree` are red-black trees.

To state the rules it helps to treat every empty child slot as a real node: a **NIL leaf**, which holds no key. (In
code, one shared sentinel node plays all of them.) The keys sit in the internal nodes. The **five rules**:

1. Every node is red or black.
2. The root is black.
3. Every NIL leaf is black.
4. A red node's children are both black (no red node has a red parent).
5. For each node, every path from it down to a NIL leaf passes the same number of black nodes.

The number in rule 5, not counting the node itself, is its **black-height** $\mathrm{bh}(x)$.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 780 290" role="img" aria-label="A red-black tree. Black root 20; its children are red 10 and black 30. Red 10 has black children 5 and 15. Black 30 has a red left child 25. Black 5 has a red left child 1. Small black squares mark the NIL leaves.">
<line x1="70" y1="220" x2="45" y2="270" stroke="currentColor" stroke-width="1"/>
<line x1="70" y1="220" x2="95" y2="270" stroke="currentColor" stroke-width="1"/>
<line x1="110" y1="160" x2="150" y2="220" stroke="currentColor" stroke-width="1"/>
<line x1="250" y1="160" x2="225" y2="220" stroke="currentColor" stroke-width="1"/>
<line x1="250" y1="160" x2="275" y2="220" stroke="currentColor" stroke-width="1"/>
<line x1="430" y1="160" x2="405" y2="220" stroke="currentColor" stroke-width="1"/>
<line x1="430" y1="160" x2="455" y2="220" stroke="currentColor" stroke-width="1"/>
<line x1="480" y1="100" x2="530" y2="160" stroke="currentColor" stroke-width="1"/>
<line x1="330" y1="40" x2="180" y2="100" stroke="currentColor" stroke-width="1.5"/>
<line x1="330" y1="40" x2="480" y2="100" stroke="currentColor" stroke-width="1.5"/>
<line x1="180" y1="100" x2="110" y2="160" stroke="currentColor" stroke-width="1.5"/>
<line x1="180" y1="100" x2="250" y2="160" stroke="currentColor" stroke-width="1.5"/>
<line x1="480" y1="100" x2="430" y2="160" stroke="currentColor" stroke-width="1.5"/>
<line x1="110" y1="160" x2="70" y2="220" stroke="currentColor" stroke-width="1.5"/>
<circle cx="330" cy="40" r="17" fill="currentColor" stroke="currentColor" stroke-width="1.2"/><text x="330" y="45" font-size="14" text-anchor="middle" style="fill:var(--md-default-bg-color)">20</text>
<circle cx="180" cy="100" r="17" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/><text x="180" y="105" font-size="14" text-anchor="middle" fill="currentColor">10</text>
<circle cx="480" cy="100" r="17" fill="currentColor" stroke="currentColor" stroke-width="1.2"/><text x="480" y="105" font-size="14" text-anchor="middle" style="fill:var(--md-default-bg-color)">30</text>
<circle cx="110" cy="160" r="17" fill="currentColor" stroke="currentColor" stroke-width="1.2"/><text x="110" y="165" font-size="14" text-anchor="middle" style="fill:var(--md-default-bg-color)">5</text>
<circle cx="250" cy="160" r="17" fill="currentColor" stroke="currentColor" stroke-width="1.2"/><text x="250" y="165" font-size="14" text-anchor="middle" style="fill:var(--md-default-bg-color)">15</text>
<circle cx="430" cy="160" r="17" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/><text x="430" y="165" font-size="14" text-anchor="middle" fill="currentColor">25</text>
<circle cx="70" cy="220" r="17" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/><text x="70" y="225" font-size="14" text-anchor="middle" fill="currentColor">1</text>
<rect x="39" y="264" width="12" height="12" fill="currentColor"/>
<rect x="89" y="264" width="12" height="12" fill="currentColor"/>
<rect x="144" y="214" width="12" height="12" fill="currentColor"/>
<rect x="219" y="214" width="12" height="12" fill="currentColor"/>
<rect x="269" y="214" width="12" height="12" fill="currentColor"/>
<rect x="399" y="214" width="12" height="12" fill="currentColor"/>
<rect x="449" y="214" width="12" height="12" fill="currentColor"/>
<rect x="524" y="154" width="12" height="12" fill="currentColor"/>
<text x="580" y="40" font-size="12" text-anchor="start" fill="currentColor">red nodes: 10, 25, 1</text>
<text x="580" y="60" font-size="12" text-anchor="start" fill="currentColor">black nodes: 20, 5, 15, 30</text>
<text x="580" y="80" font-size="12" text-anchor="start" fill="currentColor">squares: NIL leaves (black)</text>
<text x="580" y="120" font-size="12" text-anchor="start" fill="currentColor">black-height of the root: 2</text>
<text x="580" y="140" font-size="12" text-anchor="start" fill="currentColor">(on every path down, not</text>
<text x="580" y="158" font-size="12" text-anchor="start" fill="currentColor">counting the root itself)</text>
<text x="580" y="200" font-size="12" text-anchor="start" fill="currentColor">no red node has a red child</text>
</svg>
<figcaption>Figure 8.3. The red-black tree after inserting 10, 20, 30, 15, 25, 5, 1 (the trace in section 8.4). Red nodes are drawn orange, black nodes filled. Every path from the root to a NIL square passes 2 black nodes below the root, and red nodes never touch.</figcaption>
</figure>

### The height bound

In this subsection the height counts edges down to the NIL leaves, so it equals the number of key nodes on the longest
path.

**Lemma 8.3.** The subtree of any node $x$ contains at least $2^{\mathrm{bh}(x)} - 1$ key nodes.

*Proof,* by induction on the height of $x$. If $x$ is a NIL leaf, $\mathrm{bh}(x) = 0$ and it contains
$2^0 - 1 = 0$ key nodes. Otherwise each child $c$ of $x$ has black-height $\mathrm{bh}(x)$ (if $c$ is red) or
$\mathrm{bh}(x) - 1$ (if $c$ is black), so at least $\mathrm{bh}(x) - 1$; by induction each child's subtree has at
least $2^{\mathrm{bh}(x)-1} - 1$ key nodes, and with $x$ itself the total is at least
$2(2^{\mathrm{bh}(x)-1} - 1) + 1 = 2^{\mathrm{bh}(x)} - 1$. $\square$

**Theorem 8.4.** A red-black tree with $n$ keys has height at most $2\log_2(n+1)$.

*Proof.* Let $h$ be the height and take a longest path from the root down to a NIL leaf; it has $h$ nodes below the
root. By rule 4, no two reds are adjacent on it, and the NIL at the bottom is black (rule 3), so at least half of those
$h$ nodes are black: $\mathrm{bh}(\text{root}) \ge h/2$. By the lemma, $n \ge 2^{h/2} - 1$, so
$h \le 2\log_2(n+1)$. $\square$

The same argument shows something sharper: the longest root-to-NIL path is at most twice the shortest, because both
carry the same number of blacks and the longer one can at most interleave one red after each black.

### Insertion and its three cases

Insert the key as in a BST and colour the new node **red**. Why red? A red node adds nothing to any black count, so
rule 5 stays true. The only rules that can break are rule 2 (if the tree was empty, the new red node is the root) and
rule 4 (if its parent is red). The repair, called **fixup**, looks at the new node $z$, its parent $p$, its grandparent
$g$ (which exists and is black, since $p$ is red and the root is black) and its **uncle** $u$, the other child of $g$.
Assume $p$ is a left child; the other side is the mirror image.

- **Case 1: the uncle is red.** Colour $p$ and $u$ black and $g$ red. Every path through $g$ still meets one black on
  this level (before: $g$; now: $p$ or $u$), so rule 5 holds. The red-red problem may have moved up to $g$ and its
  parent, so set $z = g$ and repeat. This case does no rotation.
- **Case 2: the uncle is black and $z$ is a right child** (the path $g, p, z$ bends). Rotate left at $p$ and rename:
  the old $p$ becomes the new $z$. Now the path is straight, which is case 3. Both nodes involved are red, so no
  black count changes.
- **Case 3: the uncle is black and $z$ is a left child** (the path is straight). Colour $p$ black and $g$ red, then
  rotate right at $g$. Now $p$ is a black node at the top of this subtree, with red children $z$ and $g$. Every path
  that passed through the black $g$ now passes through the black $p$ instead, so black counts are unchanged, and there
  is no red-red pair. The loop stops.

At the very end colour the root black, which fixes rule 2 and never breaks anything else (it adds one black to every
path at once).

**Why it terminates in $O(\log n)$ with at most two rotations.** Case 1 moves $z$ up two levels, so it can repeat at
most $h/2$ times. Cases 2 and 3 happen at most once each, and after case 3 the loop ends. So an insertion costs
$O(\log n)$ time and at most **two rotations**. Deletion has four cases and needs at most **three rotations**; the
argument is the same in spirit and longer in detail (CLRS, chapter 13, gives every case).

The program prints this trace for inserting 10, 20, 30, 15, 25, 5, 1 (`R` red, `B` black):

| Insert | Tree after | What happened |
| --- | --- | --- |
| 10 | 10B | the new red root is made black |
| 20 | 10B(.,20R) | parent black: nothing to do |
| 30 | 20B(10R,30R) | parent 20 red, uncle NIL black, straight path: case 3, rotate left at 10 |
| 15 | 20B(10B(.,15R),30B) | uncle 30 red: case 1, recolour; 20 becomes red, then the root is made black again |
| 25 | 20B(10B(.,15R),30B(25R,.)) | parent black |
| 5 | 20B(10B(5R,15R),30B(25R,.)) | parent black |
| 1 | 20B(10R(5B(1R,.),15B),30B(25R,.)) | uncle 15 red: case 1 at 1; then 10 is red under a black parent, so stop |

The final tree is Figure 8.3.

```python
--8<-- "books/algorithms/ch08_red_black.py"
```

```
insert 10: 10B                                      root made black
insert 20: 10B(.,20R)                               -
insert 30: 20B(10R,30R)                             case 3 at 30
insert 15: 20B(10B(.,15R),30B)                      case 1 at 15, root made black
insert 25: 20B(10B(.,15R),30B(25R,.))               -
insert  5: 20B(10B(5R,15R),30B(25R,.))              -
insert  1: 20B(10R(5B(1R,.),15B),30B(25R,.))        case 1 at 1
n =   1000: height 12, black-height 6, 2*log2(n+1) = 19.9
n = 100000: height 20, black-height 10, 2*log2(n+1) = 33.2
sorted n = 100000: height 31
```

On 100,000 sorted keys, which turn a plain BST into a path, the red-black tree has height 31, below the bound
$2\log_2(100001) \approx 33.2$. On random keys it is closer to the floor.

### Red-black trees are 2-3-4 trees in disguise

Here is the view that makes the rules feel inevitable. Glue every red node to its black parent. Each black node with
its red children becomes a single "fat" node holding 1, 2 or 3 keys and having 2, 3 or 4 children. Rule 5 says every
path from the root to a NIL meets the same number of fat nodes, so all the leaves of the fat tree are at the same
depth: it is a perfectly balanced **2-3-4 tree**, which is the B-tree of the next section with $t = 2$. Case 1 of the
insertion (recolouring) is splitting a fat node that has become too full and pushing its middle key up; cases 2 and 3
are rearranging the keys inside one fat node. Sedgewick's **left-leaning red-black trees** (2008) take this further:
they allow red links only on the left, which makes them 2-3 trees and cuts the code to a few lines, at some cost in
speed.

**AVL or red-black?** AVL trees are shallower (at most $1.44\log_2 n$ against $2\log_2 n$), so searches are a little
faster; red-black trees do fewer rotations on updates. In practice both are fast, and red-black trees won the libraries.

## 8.5 B-trees for disks and databases

*Level: intermediate.*

A database table with a billion rows does not fit in memory. It lives on a disk or SSD, which is read in **blocks**
(pages) of a few kilobytes, and reading one block costs as much as many thousands of operations in memory. For such
data the cost that matters is not comparisons but **block reads**. A red-black tree on $10^9$ keys has height at least
29, and if every node is in a different block, one search reads around 30 blocks. Can we do better?

Yes: make each node as large as one block. A node holding 100 keys has 101 children, so the tree branches 101 ways at
each level instead of 2, and its height is about $\log_{101} n$ instead of $\log_2 n$. Rudolf Bayer and Edward
McCreight, working at Boeing's research labs, introduced these **B-trees** in 1970 (published 1972 as "Organization and
maintenance of large ordered indexes").

**Definition** (with **minimum degree** $t \ge 2$, as in CLRS):

1. Each node holds its keys in sorted order, $k_1 < k_2 < \dots < k_m$, and, if it is internal, $m+1$ children. The
   keys separate the children: all keys in child $i$ lie between $k_{i}$ and $k_{i+1}$.
2. Every node except the root holds at least $t-1$ keys; the root holds at least 1 (if the tree is not empty).
3. Every node holds at most $2t-1$ keys. A node with $2t-1$ keys is **full**.
4. All leaves have the same depth.

With $t = 2$ a node holds 1 to 3 keys and has 2 to 4 children: the 2-3-4 tree of the last section.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 760 290" role="img" aria-label="A B-tree with minimum degree 2. Root holds 40. Its children hold 20 and 60. Leaves hold 5 10 15, then 30, then 50, then 70 80 90.">
<line x1="330" y1="50" x2="157" y2="100" stroke="currentColor" stroke-width="1.5"/>
<line x1="364" y1="50" x2="517" y2="100" stroke="currentColor" stroke-width="1.5"/>
<line x1="140" y1="130" x2="81" y2="190" stroke="currentColor" stroke-width="1.5"/>
<line x1="174" y1="130" x2="207" y2="190" stroke="currentColor" stroke-width="1.5"/>
<line x1="500" y1="130" x2="427" y2="190" stroke="currentColor" stroke-width="1.5"/>
<line x1="534" y1="130" x2="571" y2="190" stroke="currentColor" stroke-width="1.5"/>
<rect x="330" y="20" width="34" height="30" rx="4" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/>
<text x="347" y="40" font-size="13" text-anchor="middle" fill="currentColor">40</text>
<rect x="140" y="100" width="34" height="30" rx="4" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="157" y="120" font-size="13" text-anchor="middle" fill="currentColor">20</text>
<rect x="500" y="100" width="34" height="30" rx="4" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="517" y="120" font-size="13" text-anchor="middle" fill="currentColor">60</text>
<rect x="30" y="190" width="102" height="30" rx="4" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<text x="47" y="210" font-size="13" text-anchor="middle" fill="currentColor">5</text>
<line x1="64" y1="190" x2="64" y2="220" stroke="currentColor" stroke-width="1"/>
<text x="81" y="210" font-size="13" text-anchor="middle" fill="currentColor">10</text>
<line x1="98" y1="190" x2="98" y2="220" stroke="currentColor" stroke-width="1"/>
<text x="115" y="210" font-size="13" text-anchor="middle" fill="currentColor">15</text>
<rect x="190" y="190" width="34" height="30" rx="4" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<text x="207" y="210" font-size="13" text-anchor="middle" fill="currentColor">30</text>
<rect x="410" y="190" width="34" height="30" rx="4" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<text x="427" y="210" font-size="13" text-anchor="middle" fill="currentColor">50</text>
<rect x="520" y="190" width="102" height="30" rx="4" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<text x="537" y="210" font-size="13" text-anchor="middle" fill="currentColor">70</text>
<line x1="554" y1="190" x2="554" y2="220" stroke="currentColor" stroke-width="1"/>
<text x="571" y="210" font-size="13" text-anchor="middle" fill="currentColor">80</text>
<line x1="588" y1="190" x2="588" y2="220" stroke="currentColor" stroke-width="1"/>
<text x="605" y="210" font-size="13" text-anchor="middle" fill="currentColor">90</text>
<text x="380" y="272" font-size="12" text-anchor="middle" fill="currentColor">t = 2: every node but the root holds 1 to 3 keys; all leaves at the same depth</text>
</svg>
<figcaption>Figure 8.4. The B-tree of minimum degree t = 2 after the insertions traced in section 8.5. A node with k keys has k + 1 children, and the keys of a node separate the key ranges of its children.</figcaption>
</figure>

**Search** is binary-search-tree search with a many-way choice at each node: binary search among the keys in the node
(in memory, cheap), then follow the right child. It reads one node per level.

**Theorem 8.5.** A B-tree with $n \ge 1$ keys and minimum degree $t$ has height $h \le \log_t\frac{n+1}{2}$.

*Proof.* Count the fewest keys a tree of height $h$ can hold. The root has at least 1 key, hence at least 2 children.
Every other internal node has at least $t$ children. So there are at least 2 nodes at depth 1, $2t$ at depth 2, and
$2t^{i-1}$ at depth $i$. Each non-root node holds at least $t-1$ keys, so

$$
n \ge 1 + (t-1)\sum_{i=1}^{h} 2t^{i-1} = 1 + 2(t-1)\cdot\frac{t^h - 1}{t-1} = 2t^h - 1 .
$$

Hence $t^h \le (n+1)/2$, and take $\log_t$. $\square$

With $t = 100$ and $n = 10^9$, $\log_{100}(5\times10^8) \approx 4.35$, so the height is at most 4 and a search reads at
most 5 nodes. The root and its children are almost always cached in memory, so a lookup in a billion-row index
typically costs two or three real block reads.

### Insertion by splitting on the way down

A new key always goes into a leaf (rule 4 forbids growing new leaves at different depths). The danger is a full leaf.
The fix is to **split**: a full node with $2t-1$ keys becomes two nodes of $t-1$ keys each, and its middle key moves up
into the parent. But then the parent might be full too, and the split would ripple up. CLRS's version avoids going
back up: on the way *down*, split every full node you are about to step into. Then the parent of any node you split is
never full, so there is room for the middle key.

- If the root is full, split it first: a new root with one key and two children appears. **This is the only way a
  B-tree grows taller**, and it raises every leaf by one level at once, which is why all leaves stay at the same depth.
- Descend; before stepping into a full child, split it.
- At the leaf (now not full) insert the key in sorted position.

Trace with $t = 2$ (at most 3 keys per node), inserting 10, 20, ..., 90, then 5 and 15. In the notation of the
program, `[...]` is a leaf and `{child key child key ...}` an internal node.

| Insert | Tree after | What happened |
| --- | --- | --- |
| 10, 20, 30 | [10 20 30] | the root leaf fills up |
| 40 | {[10] 20 [30 40]} | root full: split, 20 moves up into a new root |
| 50 | {[10] 20 [30 40 50]} | |
| 60 | {[10] 20 [30] 40 [50 60]} | child [30 40 50] full: split on the way down, 40 moves up |
| 70 | {[10] 20 [30] 40 [50 60 70]} | |
| 80 | {[10] 20 [30] 40 [50] 60 [70 80]} | split [50 60 70], 60 up; root now full |
| 90 | {{[10] 20 [30]} 40 {[50] 60 [70 80 90]}} | root full: split, 40 up, the tree grows a level |
| 5, 15 | {{[5 10 15] 20 [30]} 40 {...}} | Figure 8.4 |

**Cost:** $O(h) = O(\log_t n)$ node reads and writes, and $O(t)$ work inside each node, so $O(t\log_t n)$ operations.

**Deletion** is the mirror image: on the way down, make sure every node you step into has at least $t$ keys (one more
than the minimum), by **borrowing** a key from a sibling through the parent or **merging** with a sibling. The cases
are fiddly but each is $O(t)$, and the tree shrinks only when the root's last two children merge.

```python
--8<-- "books/algorithms/ch08_btree.py"
```

```
insert 10: [10]
insert 20: [10 20]
insert 30: [10 20 30]
insert 40: {[10] 20 [30 40]}
insert 50: {[10] 20 [30 40 50]}
insert 60: {[10] 20 [30] 40 [50 60]}
insert 70: {[10] 20 [30] 40 [50 60 70]}
insert 80: {[10] 20 [30] 40 [50] 60 [70 80]}
insert 90: {{[10] 20 [30]} 40 {[50] 60 [70 80 90]}}
insert  5: {{[5 10] 20 [30]} 40 {[50] 60 [70 80 90]}}
insert 15: {{[5 10 15] 20 [30]} 40 {[50] 60 [70 80 90]}}
t = 50, n = 500000: height 3, nodes read by a search 4, bound log_t((n+1)/2) = 3.18
a balanced binary tree on n keys: height >= 18
```

### B+ trees in real systems

Most real databases and file systems use a variant, the **B+ tree**: all the records live in the leaves, internal
nodes hold only copies of keys for routing (so more of them fit in a block), and the leaves are linked left to right
so that a range scan walks along the bottom level without going back up. The index structures of SQLite, PostgreSQL
(its default index type) and MySQL's InnoDB engine are B-tree variants of this kind, as are the directory indexes of
file systems such as NTFS, Btrfs and XFS. [Chapter 24](24-Algorithms-for-Big-Data-and-Many-Processors.md) studies the
model behind all this, the **I/O model**, in which the cost of an algorithm is the number of blocks it moves, and shows
that B-trees are optimal in it.

## 8.6 Treaps and skip lists: randomness instead of rules

*Level: advanced.*

The trees so far stay balanced by enforcing rules, and the rules need case analysis. There is another way. We saw in
8.2 that a BST built from keys in *random* order is shallow. We cannot make users insert in random order, but we can
pretend they did.

### Treaps

Give every key a random **priority** when it is inserted. A **treap** (tree plus heap) is a binary tree that is:

- a **binary search tree by key**, and
- a **heap by priority**: every node's priority is smaller than its children's priorities (the smallest priority is at
  the root; [Chapter 9](09-Heaps-and-Priority-Queues.md) is about heaps).

Raimund Seidel and Cecilia Aragon introduced treaps in 1989 ("Randomized search trees", FOCS 1989; journal version
1996). The idea of a tree that is a BST in one coordinate and a heap in another goes back to Jean Vuillemin's
**Cartesian trees** (1980).

**Lemma 8.6.** If keys and priorities are all distinct, exactly one treap holds them, and it is the BST you get by
inserting the keys in order of increasing priority.

*Proof.* The root must have the smallest priority (heap rule). Then every smaller key must go into the left subtree and
every larger key into the right one (BST rule), so the split is forced, and by induction each side is forced too. That
is exactly what plain BST insertion does when the key with the smallest priority is inserted first. $\square$

So a treap with random priorities has the shape of a BST built in random order, whatever order the keys arrived in.

**Insertion:** insert by key as in a BST, as a leaf; then, while the new node's priority is smaller than its parent's,
rotate it up (a right rotation if it is a left child, a left rotation otherwise). Each rotation keeps the BST order
(Figure 8.2) and fixes the heap order between the two nodes. **Deletion:** rotate the node down, always lifting the
child with the smaller priority, until it is a leaf, then cut it off.

Trace with keys and priorities chosen by hand (the program prints the same thing as `key:priority`):

| Insert | Treap after | What happened |
| --- | --- | --- |
| D:9 | D:9 | |
| B:4 | B:4(.,D:9) | B goes left of D, then 4 < 9: rotate right, B goes up |
| F:7 | B:4(.,F:7(D:9,.)) | F goes right of D; 7 < 9: rotate left at D |
| A:6 | B:4(A:6,F:7(D:9,.)) | A goes left of B; 6 > 4: stays |
| C:2 | C:2(B:4(A:6,.),F:7(D:9,.)) | C lands left of D, then rotates up three times to the root |
| E:1 | E:1(C:2(B:4(A:6,.),D:9),F:7) | E lands right of D and rotates up to the root |

The final treap is the BST of inserting E, C, B, A, F, D: increasing priority, as the lemma says.

**Theorem 8.7.** In a treap on keys $1, \dots, n$ with independent uniformly random priorities, the expected depth of
key $k$ is $H_k + H_{n-k+1} - 2 < 2\ln n$, where $H_m = 1 + \frac12 + \dots + \frac1m$ is the harmonic number.

*Proof.* The depth of $k$ is the number of its proper ancestors. For each $i \ne k$, let $A_{ik}$ be 1 if $i$ is an
ancestor of $k$ and 0 otherwise. Then depth$(k) = \sum_{i \ne k} A_{ik}$, and by linearity of expectation (which needs
no independence) the expected depth is $\sum_{i\ne k}\Pr[A_{ik} = 1]$.

*Claim:* $i$ is an ancestor of $k$ exactly when $i$ has the smallest priority among all the keys between $i$ and $k$
inclusive. Think of building the treap by inserting in priority order (Lemma 8.6). Until some key in the range
$[\min(i,k), \max(i,k)]$ is inserted, $i$ and $k$ fall on the same side of every node above them. The first key of the
range to be inserted separates them for good. If that key is $i$, then $k$ is inserted later into $i$'s subtree, so
$i$ is an ancestor. If it is $k$, then $k$ is an ancestor of $i$, not the other way. If it is some key strictly between,
$i$ and $k$ end up in different subtrees of it, and neither is an ancestor of the other.

The range has $|i - k| + 1$ keys, and each is equally likely to have the smallest priority, so
$\Pr[A_{ik} = 1] = 1/(|i-k|+1)$. Summing over $i < k$ gives $\frac12 + \frac13 + \dots + \frac1k = H_k - 1$, and over
$i > k$ gives $H_{n-k+1} - 1$. Since $H_m \le 1 + \ln m$, the total is below $2\ln n$. $\square$

The same proof gives expected $O(\log n)$ for search, insert and delete, and one more useful fact: an insertion or
deletion does fewer than **2 rotations on average** (Seidel and Aragon), because a new node usually lands near the
bottom and stays there. The expected *height* is also $O(\log n)$, with high probability (the full proof uses the tail
bounds of [Chapter 21](21-Randomized-and-Amortized-Analysis.md)).

Treaps also make **split** (cut a treap into keys below $x$ and keys above $x$) and **join** (glue two treaps when all
keys of one are smaller) easy: insert a dummy key $x$ with priority $-\infty$, it rotates to the root, and its two
subtrees are the answer. That is why treaps are popular in programming contests for "implicit" sequences that are cut
and pasted.

### Skip lists

William Pugh's **skip list** (1990, "Skip lists: a probabilistic alternative to balanced trees") gets the same effect
with linked lists and no rotations at all.

Start from a sorted linked list: searching it takes $O(n)$. Now add an "express lane": a second list that links every
other node. Add a third linking every fourth node, and so on. Searching runs along the top lane until the next node
would overshoot, drops a level, and repeats, like binary search. Keeping exactly "every other node" under insertions
would be expensive, so Pugh made it random: **each new node gets level 1, and then one more level for each coin flip
that comes up heads.** A node reaches level $\ell$ with probability $2^{-(\ell-1)}$.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 760 240" role="img" aria-label="A skip list of 10, 20, 30, 40, 50, 60, 70. The bottom level links all seven keys. Level 2 links 10, 20, 40, 50, 60. Level 3 links 10 and 50.">
<rect x="20" y="155" width="60" height="30" rx="4" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/>
<text x="50" y="175" font-size="12" text-anchor="middle" fill="currentColor">head</text>
<text x="15" y="175" font-size="11" text-anchor="end" fill="currentColor">L1</text>
<line x1="80" y1="170" x2="89.0" y2="170.0" stroke="currentColor" stroke-width="1.2"/><polygon points="98,170 89.0,174.0 89.0,166.0" fill="currentColor"/>
<line x1="142" y1="170" x2="169.0" y2="170.0" stroke="currentColor" stroke-width="1.2"/><polygon points="178,170 169.0,174.0 169.0,166.0" fill="currentColor"/>
<line x1="222" y1="170" x2="249.0" y2="170.0" stroke="currentColor" stroke-width="1.2"/><polygon points="258,170 249.0,174.0 249.0,166.0" fill="currentColor"/>
<line x1="302" y1="170" x2="329.0" y2="170.0" stroke="currentColor" stroke-width="1.2"/><polygon points="338,170 329.0,174.0 329.0,166.0" fill="currentColor"/>
<line x1="382" y1="170" x2="409.0" y2="170.0" stroke="currentColor" stroke-width="1.2"/><polygon points="418,170 409.0,174.0 409.0,166.0" fill="currentColor"/>
<line x1="462" y1="170" x2="489.0" y2="170.0" stroke="currentColor" stroke-width="1.2"/><polygon points="498,170 489.0,174.0 489.0,166.0" fill="currentColor"/>
<line x1="542" y1="170" x2="569.0" y2="170.0" stroke="currentColor" stroke-width="1.2"/><polygon points="578,170 569.0,174.0 569.0,166.0" fill="currentColor"/>
<line x1="622" y1="170" x2="681.0" y2="170.0" stroke="currentColor" stroke-width="1.2"/><polygon points="690,170 681.0,174.0 681.0,166.0" fill="currentColor"/>
<rect x="20" y="95" width="60" height="30" rx="4" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/>
<text x="50" y="115" font-size="12" text-anchor="middle" fill="currentColor">head</text>
<text x="15" y="115" font-size="11" text-anchor="end" fill="currentColor">L2</text>
<line x1="80" y1="110" x2="89.0" y2="110.0" stroke="currentColor" stroke-width="1.2"/><polygon points="98,110 89.0,114.0 89.0,106.0" fill="currentColor"/>
<line x1="142" y1="110" x2="169.0" y2="110.0" stroke="currentColor" stroke-width="1.2"/><polygon points="178,110 169.0,114.0 169.0,106.0" fill="currentColor"/>
<line x1="222" y1="110" x2="329.0" y2="110.0" stroke="currentColor" stroke-width="1.2"/><polygon points="338,110 329.0,114.0 329.0,106.0" fill="currentColor"/>
<line x1="382" y1="110" x2="409.0" y2="110.0" stroke="currentColor" stroke-width="1.2"/><polygon points="418,110 409.0,114.0 409.0,106.0" fill="currentColor"/>
<line x1="462" y1="110" x2="489.0" y2="110.0" stroke="currentColor" stroke-width="1.2"/><polygon points="498,110 489.0,114.0 489.0,106.0" fill="currentColor"/>
<line x1="542" y1="110" x2="681.0" y2="110.0" stroke="currentColor" stroke-width="1.2"/><polygon points="690,110 681.0,114.0 681.0,106.0" fill="currentColor"/>
<rect x="20" y="35" width="60" height="30" rx="4" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/>
<text x="50" y="55" font-size="12" text-anchor="middle" fill="currentColor">head</text>
<text x="15" y="55" font-size="11" text-anchor="end" fill="currentColor">L3</text>
<line x1="80" y1="50" x2="89.0" y2="50.0" stroke="currentColor" stroke-width="1.2"/><polygon points="98,50 89.0,54.0 89.0,46.0" fill="currentColor"/>
<line x1="142" y1="50" x2="409.0" y2="50.0" stroke="currentColor" stroke-width="1.2"/><polygon points="418,50 409.0,54.0 409.0,46.0" fill="currentColor"/>
<line x1="462" y1="50" x2="681.0" y2="50.0" stroke="currentColor" stroke-width="1.2"/><polygon points="690,50 681.0,54.0 681.0,46.0" fill="currentColor"/>
<rect x="98" y="155" width="44" height="30" rx="4" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<text x="120" y="175" font-size="13" text-anchor="middle" fill="currentColor">10</text>
<rect x="98" y="95" width="44" height="30" rx="4" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="120" y="115" font-size="13" text-anchor="middle" fill="currentColor">10</text>
<rect x="98" y="35" width="44" height="30" rx="4" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="120" y="55" font-size="13" text-anchor="middle" fill="currentColor">10</text>
<rect x="178" y="155" width="44" height="30" rx="4" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<text x="200" y="175" font-size="13" text-anchor="middle" fill="currentColor">20</text>
<rect x="178" y="95" width="44" height="30" rx="4" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="200" y="115" font-size="13" text-anchor="middle" fill="currentColor">20</text>
<rect x="258" y="155" width="44" height="30" rx="4" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<text x="280" y="175" font-size="13" text-anchor="middle" fill="currentColor">30</text>
<rect x="338" y="155" width="44" height="30" rx="4" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<text x="360" y="175" font-size="13" text-anchor="middle" fill="currentColor">40</text>
<rect x="338" y="95" width="44" height="30" rx="4" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="360" y="115" font-size="13" text-anchor="middle" fill="currentColor">40</text>
<rect x="418" y="155" width="44" height="30" rx="4" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<text x="440" y="175" font-size="13" text-anchor="middle" fill="currentColor">50</text>
<rect x="418" y="95" width="44" height="30" rx="4" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="440" y="115" font-size="13" text-anchor="middle" fill="currentColor">50</text>
<rect x="418" y="35" width="44" height="30" rx="4" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="440" y="55" font-size="13" text-anchor="middle" fill="currentColor">50</text>
<rect x="498" y="155" width="44" height="30" rx="4" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<text x="520" y="175" font-size="13" text-anchor="middle" fill="currentColor">60</text>
<rect x="498" y="95" width="44" height="30" rx="4" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="520" y="115" font-size="13" text-anchor="middle" fill="currentColor">60</text>
<rect x="578" y="155" width="44" height="30" rx="4" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<text x="600" y="175" font-size="13" text-anchor="middle" fill="currentColor">70</text>
<text x="720" y="175" font-size="12" text-anchor="middle" fill="currentColor">end</text>
<text x="720" y="115" font-size="12" text-anchor="middle" fill="currentColor">end</text>
<text x="720" y="55" font-size="12" text-anchor="middle" fill="currentColor">end</text>
<text x="380" y="222" font-size="12" text-anchor="middle" fill="currentColor">search 60: right to 10, right to 50, next is the end so drop to L2, right to 60</text>
</svg>
<figcaption>Figure 8.5. A skip list built by the program in section 8.6. Each key is copied up one more level with probability 1/2. A search runs right along the top level and drops down whenever the next key would overshoot.</figcaption>
</figure>

**Search** for $k$: start at the head on the top level. At each level move right while the next key is less than $k$;
then drop one level. At level 1 the next node is $k$ if $k$ is present. **Insert**: search, remembering at each level
the last node before $k$ (the `update` list in the code); flip coins for the new node's level and splice it into each
of those lists. **Delete** is the same splice in reverse. No rebalancing is ever needed.

**Expected space.** A node has on average $1 + \frac12 + \frac14 + \dots = 2$ levels, so the expected total number of
pointers is $2n$.

**Expected number of levels.** A given node reaches level $\ell$ with probability $2^{1-\ell}$, so the chance that *any*
of the $n$ nodes does is at most $n2^{1-\ell}$ (the union bound: the chance that at least one of several events happens
is at most the sum of their chances). For $\ell = \log_2 n + 1 + c$ this is at most $2^{-c}$. So the number of levels
is $\log_2 n + O(1)$ in expectation, and above $\log_2 n + 11$ with probability below one in a thousand.

**Expected search cost**, by **backward analysis**: follow the search path in reverse, from the node found at level 1
back to the head at the top. At each node on the reversed path, either the node has a level above the current one, in
which case the reversed path goes up, or it does not, in which case the path goes left. Each node's coin flips are
independent, so each step goes up with probability $1/2$ and left with probability $1/2$ (as long as we have not reached
the head). Climbing one level therefore takes 2 steps on average (a geometric distribution), and climbing
$\log_2 n + O(1)$ levels takes $2\log_2 n + O(1)$ expected steps. Search, insert and delete all cost expected
$O(\log n)$.

```python
--8<-- "books/algorithms/ch08_treap_skiplist.py"
```

```
insert D:9  D:9
insert B:4  B:4(.,D:9)
insert F:7  B:4(.,F:7(D:9,.))
insert A:6  B:4(A:6,F:7(D:9,.))
insert C:2  C:2(B:4(A:6,.),F:7(D:9,.))
insert E:1  E:1(C:2(B:4(A:6,.),D:9),F:7)
treap, n = 100000 sorted keys: average depth 19.6, max depth 39, 2 ln n = 23.0
level 3: [10, 50]
level 2: [10, 20, 40, 50, 60]
level 1: [10, 20, 30, 40, 50, 60, 70]
skip list, n = 100000: 16 levels, average forward steps per search 14.5, 2*log2(n) = 33.2, found 94
```

The treap on 100,000 *sorted* keys has average depth 19.6, near the theory's $2(1+\frac1n)H_n - 4 \approx 20.2$ for the
average over all nodes; a plain BST on the same input would have average depth 50,000. The skip list search used fewer
forward steps than the $2\log_2 n$ bound, which counts the downward steps too.

Skip lists are simple to make **concurrent**, because an insertion changes only a few nearby pointers and never
rotates; Java's `ConcurrentSkipListMap` is one, and the in-memory database Redis uses skip lists for its sorted sets.

## 8.7 Splay trees: self-adjusting

*Level: advanced.*

Every tree so far stores extra information (heights, colours, priorities, levels) and works to keep its worst path
short. Daniel Sleator and Robert Tarjan asked in 1985 ("Self-adjusting binary search trees", *Journal of the ACM*):
what if we store nothing and never check balance, but **move every key we touch to the root**? Keys used often then
stay near the top, and long paths get shortened as a side effect of walking them.

To **splay** node $x$, repeat until $x$ is the root, with $p$ its parent and $g$ its grandparent:

- **zig**: $p$ is the root. Rotate at $p$ to lift $x$ (one rotation).
- **zig-zig**: $x$ and $p$ are both left children (or both right). Rotate $p$ above $g$ first, then $x$ above $p$.
- **zig-zag**: $x$ is a left child and $p$ a right child, or the reverse. Rotate $x$ above $p$, then $x$ above $g$
  (the same double rotation as the AVL LR case).

A search splays the node it finds (or the last node it touched, if the key is missing); an insertion splays the new
node; a deletion splays the node, removes the root, and joins the two subtrees.

The order of rotations in zig-zig is the whole secret. Rotating $x$ up one level at a time (always "rotate $x$ above
its parent") would also bring $x$ to the root, but on a path it leaves a path, and repeated accesses can cost
$\Theta(n)$ each. Zig-zig rotates the *grandparent* first, and that roughly halves the depth of every node on the
access path. The program shows it: on the path $7, 6, \dots, 1$, splaying 1 takes three zig-zig steps and leaves a tree
of height 4; on a path of 2000 nodes, after splaying the deepest key, the key that was second deepest is now at depth
1000 instead of 1998.

```python
--8<-- "books/algorithms/ch08_splay.py"
```

```
start      : 7(6(5(4(3(2(1,.),.),.),.),.),.)
find 1     : 1(.,6(4(2(.,3),5),7))  steps: zig-zig, zig-zig, zig-zig
find 4     : 4(1(.,2(.,3)),6(5,7))  steps: zig-zag
path of 2000: depth of key 1 before = 1999
after splaying 1: depth of key 2 = 1000, of key 1000 = 501
100000 uniform finds on n = 20000: 17.7 rotations per find
100000 finds among 10 hot keys: 2.5 rotations per find
```

**What is proved.** A single splay can cost $\Theta(n)$ (the first access to the path above costs 1999 rotations), so
no per-operation bound holds. But Sleator and Tarjan proved an **amortized** bound ([Chapter 4](04-Lists-Stacks-and-Queues.md)
introduced amortized analysis):

**Theorem 8.8** (Sleator and Tarjan 1985, stated here without proof). Any sequence of $m$ search, insert and delete
operations on an initially empty splay tree, with at most $n$ keys at any time, costs $O(m\log n)$ in total, so
$O(\log n)$ amortized per operation.

The proof uses the **potential method**: the potential of the tree is $\sum_x \log_2 s(x)$, where $s(x)$ is the number
of nodes in $x$'s subtree. The **access lemma** says a splay of $x$ costs at most $3(\log_2 s(\text{root}) - \log_2 s(x)) + 1$
amortized, and each zig-zig or zig-zag step pays for its two rotations out of the drop in potential. The full proof is
in [Chapter 21](21-Randomized-and-Amortized-Analysis.md), section 21.6.

Splay trees prove more than $O(\log n)$. If key $i$ is accessed $q_i$ times out of $m$, the total cost is
$O(m + \sum_i q_i\log(m/q_i))$, as good as the best *fixed* BST for those frequencies, built knowing them in advance
(the **static optimality theorem**). They also have the **working-set property**: accessing a key that was used
recently is cheap. In the last line of the program, finds among 10 hot keys cost 2.5 rotations each, against 17.7 for
uniform finds over 20,000 keys. The **dynamic optimality conjecture**, posed in the same 1985 paper, says splay trees
are within a constant factor of the best possible BST algorithm on *every* access sequence. It is still open.

Splay trees are used where access patterns are skewed and the code must be short: caches, some memory allocators, the
"rope" data structures of text editors. The cost is that even a search changes the tree, which is bad for concurrent
readers and for cache memory.

## 8.8 Which tree to use

| Structure | Height or cost | Extra per node | Good for |
| --- | --- | --- | --- |
| plain BST | $O(n)$ worst, $O(\log n)$ expected on random input | none | teaching; data known to be random |
| AVL | $\le 1.44\log_2 n$ | a height | lookups much more frequent than updates |
| red-black | $\le 2\log_2(n+1)$; $O(1)$ rotations per update | 1 bit | general ordered maps in libraries |
| B-tree, B+ tree | $\le\log_t\frac{n+1}{2}$ levels | many keys per node | disks, SSDs, databases, file systems |
| treap | expected $O(\log n)$ | a priority | short code, split and join |
| skip list | expected $O(\log n)$ | about 2 pointers on average | concurrency |
| splay | $O(\log n)$ amortized | none | skewed or repeating access patterns |

In practice, in Python, the standard library has no balanced tree at all: `dict` and `set` are hash tables, and for
ordered data people keep a sorted list with the `bisect` module or use the third-party `sortedcontainers` package,
which stores a list of sorted lists (a cousin of a B-tree with one level). Java has `TreeMap` (red-black) and
`ConcurrentSkipListMap`; C++ has `std::map` (red-black in the common implementations).

Even on Mars these trees work without anyone watching. A rover's planner keeps its candidate waypoints and obstacles
in ordered structures it must update thousands of times between commands from Earth, which arrive 4 to 24 minutes
late; whatever order the data comes in, the worst-case bounds of this chapter are what make the timing predictable.

## Check yourself

??? question "1. Insert 5, 2, 8, 1, 3, 9, 7 into an empty BST. Give the four traversals."

    The tree is `5(2(1,3),8(7,9))`: 5 at the root, 2 and 8 below it, 1 and 3 under 2, 7 and 9 under 8.

    - preorder: 5, 2, 1, 3, 8, 7, 9
    - inorder: 1, 2, 3, 5, 7, 8, 9 (sorted, as Theorem 8.1 says)
    - postorder: 1, 3, 2, 7, 9, 8, 5
    - level order: 5, 2, 8, 1, 3, 7, 9

??? question "2. A binary tree has height 4. What is the largest and the smallest number of nodes it can have?"

    Largest: $2^{4+1} - 1 = 31$ (every level full: 1, 2, 4, 8, 16). Smallest: 5, one node per depth (a path).

??? question "3. Of the 6 orders in which 1, 2, 3 can be inserted into an empty BST, how many give a tree of height 1?"

    Height 1 means 2 is the root with 1 and 3 below. That needs 2 first; the other two can come in either order:
    (2, 1, 3) and (2, 3, 1). So 2 of the 6 orders, and the other 4 give paths of height 2.

??? question "4. Insert 1, 2, 3, 4, 5, 6, 7 into an empty AVL tree. Which rotations happen and what is the final tree?"

    Inserting 3 makes 1 unbalanced (balance $-2$, right-right): rotate left, giving `2(1,3)`. Inserting 5 unbalances 3:
    rotate left, `2(1,4(3,5))`. Inserting 6 unbalances the root 2: rotate left, `4(2(1,3),5(.,6))`. Inserting 7
    unbalances 5: rotate left, giving the perfect tree `4(2(1,3),6(5,7))` of height 2. Four single left rotations,
    no double rotations. (Run `ch08_avl.py` with these keys to check.)

??? question "5. What is the fewest nodes an AVL tree of height 6 can have? And what is the tallest AVL tree on 100 nodes?"

    $N(6) = F(9) - 1 = 34 - 1 = 33$ (the program's table also gives 33). For the tallest tree on 100 nodes, find the
    largest $h$ with $N(h) \le 100$: $N(7) = 54$, $N(8) = 54 + 33 + 1 = 88$, $N(9) = 88 + 54 + 1 = 143$. So the height is
    at most 8. Compare the floor $\lceil\log_2 101\rceil - 1 = 6$.

??? question "6. Prove that in a red-black tree the longest path from a node down to a NIL leaf is at most twice as long as the shortest."

    Let both paths start at $x$ and let $b = \mathrm{bh}(x)$. By rule 5 both paths contain exactly $b$ black nodes below
    $x$ (counting the NIL). The shortest path has at least $b$ nodes. On the longest path, rule 4 forbids two reds in
    a row, and the last node (NIL) is black, so each red can be paired with the black right after it: at most $b$
    reds, so at most $2b$ nodes. Hence longest $\le 2b \le 2\cdot$ shortest.

??? question "7. A student checks a BST by testing, at every node, that the left child is smaller and the right child larger. Give a tree that passes the test but is not a BST, and write a correct check."

    `5(3(.,7),8)`: at 5, 3 < 5 < 8; at 3, its right child 7 > 3. Every local test passes, but 7 is in the left subtree
    of 5 and is larger than 5, so searching for 7 goes right from 5 and fails. A correct check passes down the range
    each subtree must lie in:

    ```python
    def is_bst(t, lo=float("-inf"), hi=float("inf")):
        return t is None or (lo < t.key < hi and is_bst(t.left, lo, t.key)
                             and is_bst(t.right, t.key, hi))
    ```

??? question "8. A B-tree index has minimum degree t = 100 and holds a billion keys. At most how many nodes does a search read?"

    By Theorem 8.5, $h \le \log_{100}\frac{10^9+1}{2} \approx 4.35$, so $h \le 4$ and a search reads at most
    $h + 1 = 5$ nodes. A red-black tree on the same keys would be at least 29 levels deep.

??? question "9. In a treap on keys 1 to n with random priorities, what is the probability that key 1 is an ancestor of key n? What is the expected depth of key 1?"

    By the claim in Theorem 8.7, 1 is an ancestor of $n$ exactly when 1 has the smallest priority of all $n$ keys:
    probability $1/n$. The expected depth of key 1 is $H_1 + H_n - 2 = H_n - 1$, about $\ln n - 0.42$: the left spine
    of a random BST has expected length $H_n - 1$.

??? question "10. Write the code: store in each node the size of its subtree, and use it to find the k-th smallest key in O(h)."

    Keep `size = 1 + size(left) + size(right)` up to date in `insert`. To find the $k$-th smallest: if the left
    subtree has $s$ nodes and $k = s+1$, it is the root; if $k \le s$, look for the $k$-th in the left subtree;
    otherwise the $(k - s - 1)$-th in the right subtree. Each step goes one level down.

    ```python
    class Node:
        def __init__(self, key):
            self.key, self.left, self.right, self.size = key, None, None, 1

    def size(t):
        return t.size if t else 0

    def insert(t, k):
        if t is None:
            return Node(k)
        if k < t.key:
            t.left = insert(t.left, k)
        else:
            t.right = insert(t.right, k)
        t.size = 1 + size(t.left) + size(t.right)
        return t

    def kth(t, k):                     # k = 1 gives the smallest
        while t:
            s = size(t.left)
            if k == s + 1:
                return t.key
            if k <= s:
                t = t.left
            else:
                k, t = k - s - 1, t.right
        raise IndexError(k)

    root = None
    for x in [8, 3, 10, 1, 6, 14, 4, 7, 13]:
        root = insert(root, x)
    print([kth(root, k) for k in range(1, 10)])   # [1, 3, 4, 6, 7, 8, 10, 13, 14]
    ```

    This is an **order-statistic tree**. In a balanced tree, rotations must also fix the two sizes they touch, which
    is $O(1)$ each.

??? question "11. Write the code: rebuild a BST from its preorder list alone, in O(n)."

    In preorder the first key is the root; the keys that follow and are smaller form the left subtree, the rest the
    right. Instead of searching for the split, pass down the range a subtree may occupy and consume keys from the list
    while they fit:

    ```python
    def from_preorder(pre):
        i = 0
        def build(lo, hi):
            nonlocal i
            if i == len(pre) or not lo < pre[i] < hi:
                return None
            t = Node(pre[i]); i += 1
            t.left = build(lo, t.key)
            t.right = build(t.key, hi)
            return t
        return build(float("-inf"), float("inf"))
    ```

    On `[8, 3, 1, 6, 4, 7, 10, 14, 13]` it rebuilds Figure 8.1, `8(3(1,6(4,7)),10(.,14(13,.)))`. Each key is consumed
    once and each call either consumes a key or returns at once, so the time is $O(n)$.

??? question "12. Why does a red-black insertion colour the new node red rather than black?"

    A new black node would add one black to every path through it and break rule 5 along a whole branch, which is hard
    to repair. A new red node keeps every black count, so rule 5 holds; only rule 4 (red parent) or rule 2 (empty tree)
    can break, and those are local problems that the three cases fix by moving up the tree.

## What you learned

- A binary tree of height $h$ holds at most $2^{h+1} - 1$ nodes, so $n$ nodes need height at least about $\log_2 n$;
  a plain BST can reach $n - 1$.
- The search-tree property makes the inorder walk sorted, and makes search, insert, delete, min, successor and range
  queries cost $O(h)$.
- Rotations change the shape but not the inorder sequence; every balanced tree is built on them.
- AVL trees keep height at most $1.44\log_2 n$ (the Fibonacci argument); red-black trees at most $2\log_2(n+1)$ (the
  black-height argument), with $O(1)$ rotations per update.
- B-trees branch hundreds of ways to make disk searches a few block reads deep; they grow only at the root.
- Treaps and skip lists get expected $O(\log n)$ from random priorities or coin flips, proved with indicator variables
  and backward analysis.
- Splay trees store nothing, move each accessed key to the root, and cost $O(\log n)$ amortized; whether they are
  dynamically optimal is open.

**Next:** [Chapter 9](09-Heaps-and-Priority-Queues.md), heaps and priority queues: trees that only need to know the
smallest key, and are faster for it.

## Further reading

- T. H. Cormen, C. E. Leiserson, R. L. Rivest and C. Stein, *Introduction to Algorithms*, 4th ed., 2022: chapters 12
  (binary search trees), 13 (red-black trees) and 18 (B-trees).
- R. Sedgewick and K. Wayne, *Algorithms*, 4th ed., 2011: chapter 3.3, balanced search trees, built from 2-3 trees.
- D. E. Knuth, *The Art of Computer Programming*, vol. 3, *Sorting and Searching*, 2nd ed., 1998: section 6.2 (search
  trees, including the analysis of random BSTs and AVL trees).
- G. M. Adelson-Velsky and E. M. Landis, "An algorithm for the organization of information", 1962.
- R. Bayer, "Symmetric binary B-trees: data structure and maintenance algorithms", *Acta Informatica*, 1972.
- L. J. Guibas and R. Sedgewick, "A dichromatic framework for balanced trees", FOCS 1978.
- R. Bayer and E. McCreight, "Organization and maintenance of large ordered indexes", *Acta Informatica*, 1972.
- R. Seidel and C. R. Aragon, "Randomized search trees", *Algorithmica*, 1996.
- W. Pugh, "Skip lists: a probabilistic alternative to balanced trees", *Communications of the ACM*, 1990.
- D. D. Sleator and R. E. Tarjan, "Self-adjusting binary search trees", *Journal of the ACM*, 1985.
- L. Devroye, "A note on the height of binary search trees", *Journal of the ACM*, 1986.
- On this site: the reference pages [binary search tree](../../data-structures/bst.md),
  [binary heap](../../data-structures/binary-heap.md) and [trie](../../data-structures/trie.md) (a tree for strings,
  which [Chapter 18](18-String-Algorithms.md) uses); the [Fibonacci page](../../dp/fibonacci.md) for the numbers of
  8.3; and the [Machine learning book](../index.md), where decision trees are a different kind of
  tree built from data.
