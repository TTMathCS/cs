# 9. Heaps and priority queues

*A hospital emergency room does not treat patients in the order they arrive; it treats the most urgent first, and new
patients keep arriving. An operating system picks the next process to run, a network router the next packet, a
simulation the next event in time, a route planner the next closest place. All of them need the same thing: a
collection that you can keep adding to, and from which you can always remove the item with the smallest (or largest)
key. That collection is a **priority queue**. A search tree from [Chapter 8](08-Trees-and-Balanced-Search-Trees.md)
can do it, but it keeps far more order than we need. This chapter builds the **heap**, which keeps just enough order
to find the minimum, fits in a plain array, and builds itself from $n$ items in linear time. Then it builds the heaps
that graph algorithms want: indexed heaps with decrease-key, heaps that merge quickly, and the famous Fibonacci heap,
with the honest story of why it is rarely used.*

!!! abstract "In this chapter"
    **You will learn:**

    - what a priority queue is, and what each operation costs on lists, trees and heaps
    - how a binary heap lives in an array, how sift-up and sift-down work, and the proof that build-heap is $O(n)$
    - heapsort in place, and how $d$-ary heaps trade a cheap push for a dearer pop
    - decrease-key with an indexed heap, and the lazy-deletion trick that Python programmers use instead
    - mergeable heaps: leftist heaps (the right-spine bound) and binomial heaps (merging is binary addition)
    - the Fibonacci heap's amortized bounds proved with a potential function, why its degrees are Fibonacci-bounded, and
      why pairing heaps or plain binary heaps usually win in practice

    **You need:** [Chapter 2](02-Measuring-Cost.md) (sums, $O$-notation), [Chapter 4](04-Lists-Stacks-and-Queues.md)
    (arrays, amortized analysis and the potential method), [Chapter 8](08-Trees-and-Balanced-Search-Trees.md) (trees,
    heights). Dijkstra's algorithm appears as an example; [Chapter 16](16-Shortest-Paths.md) proves it correct.

    **Levels:** 9.1 to 9.3 are beginner to intermediate; 9.4 is intermediate; 9.5 is advanced; 9.6 is expert.

## 9.1 The priority-queue problem

A **priority queue** holds items, each with a **key** (its priority), and supports:

- **insert** (or push): add an item with a key;
- **find-min** (or peek): report an item with the smallest key;
- **extract-min** (or pop): remove and return an item with the smallest key.

Many uses also want:

- **decrease-key**: make one item's key smaller (a shortcut to it was found);
- **delete**: remove an arbitrary item;
- **meld** (or merge, union): combine two priority queues into one.

A **max**-priority queue is the same with "largest" in place of "smallest"; one turns into the other by negating keys.
The **ADT** (abstract data type: the list of operations and what they promise, as in
[Chapter 4](04-Lists-Stacks-and-Queues.md)) says nothing about how it is stored. Here are the obvious stores:

| Store | insert | find-min | extract-min | build from $n$ items |
| --- | --- | --- | --- | --- |
| unsorted list | $O(1)$ | $O(n)$ | $O(n)$ | $O(n)$ |
| sorted list (smallest at the end) | $O(n)$ | $O(1)$ | $O(1)$ | $O(n\log n)$ |
| balanced search tree | $O(\log n)$ | $O(\log n)$, or $O(1)$ with a pointer | $O(\log n)$ | $O(n\log n)$ |
| **binary heap** (9.2) | $O(\log n)$ | $O(1)$ | $O(\log n)$ | $O(n)$ |

The list solutions put all the work on one side. The search tree is balanced in cost, but it keeps *every* key in
order, so it pays for the ability to answer "what is the successor of 42?", which a priority queue never asks. The heap
gives up that ability and gets a simpler structure, smaller constants, and linear-time building.

**A lower bound.** No comparison-based priority queue can make both insert and extract-min $o(\log n)$. If it could, we
could sort $n$ items by $n$ inserts and $n$ extract-mins in $o(n\log n)$ comparisons, contradicting the
$\Omega(n\log n)$ sorting lower bound of [Chapter 5](05-Sorting-by-Comparison.md). So $O(\log n)$ for the pair is the
best possible, and the cleverer heaps of 9.5 and 9.6 can only move cost between operations, not remove it.

## 9.2 Binary heaps in an array

How little order is enough to find the minimum quickly? Keep a binary tree in which **every parent's key is at most
its children's keys**. That is the **heap property** (for a min-heap). Following parents up from any node, keys only
go down, so the root holds the minimum. Nothing is said about the order of siblings or cousins: the tree is only
"sorted along each path".

To keep the height small, a **binary heap** also fixes the **shape**: it is a **complete binary tree**, with every level
full except possibly the last, which is filled from the left. A complete tree with $n$ nodes has height
$\lfloor\log_2 n\rfloor$: levels $0$ to $h-1$ are full, holding $2^h - 1$ nodes, and level $h$ has at least one, so
$2^h \le n < 2^{h+1}$.

The shape has a bonus. Number the nodes level by level, left to right, starting at 0, and store node $i$ in position
$i$ of an array (a Python list). Then

- the children of position $i$ are at $2i+1$ and $2i+2$,
- the parent of position $i > 0$ is at $\lfloor (i-1)/2\rfloor$.

*Why:* level $d$ starts at position $2^d - 1$. If $i$ is the $j$-th node of level $d$ (counting from 0), then
$i = 2^d - 1 + j$, and its left child is the $2j$-th node of level $d+1$, at position $2^{d+1} - 1 + 2j = 2i + 1$.
No pointers are stored at all: the tree is implicit in the arithmetic.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 780 262" role="img" aria-label="A min-heap drawn as a tree, root 1, then 3 and 2, then 4, 8, 7, 6, then 9 and 5, each node labelled with its list index 0 to 8. On the right the same values in a list, with curved arrows from index 1 to its children at indexes 3 and 4.">
<line x1="200" y1="40" x2="110" y2="100" stroke="currentColor" stroke-width="1.5"/>
<line x1="200" y1="40" x2="290" y2="100" stroke="currentColor" stroke-width="1.5"/>
<line x1="110" y1="100" x2="60" y2="160" stroke="currentColor" stroke-width="1.5"/>
<line x1="110" y1="100" x2="160" y2="160" stroke="currentColor" stroke-width="1.5"/>
<line x1="290" y1="100" x2="240" y2="160" stroke="currentColor" stroke-width="1.5"/>
<line x1="290" y1="100" x2="340" y2="160" stroke="currentColor" stroke-width="1.5"/>
<line x1="60" y1="160" x2="35" y2="220" stroke="currentColor" stroke-width="1.5"/>
<line x1="60" y1="160" x2="85" y2="220" stroke="currentColor" stroke-width="1.5"/>
<circle cx="200" cy="40" r="17" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/><text x="200" y="45" font-size="14" text-anchor="middle" fill="currentColor">1</text>
<text x="200" y="70" font-size="10" text-anchor="middle" fill="currentColor">[0]</text>
<circle cx="110" cy="100" r="17" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/><text x="110" y="105" font-size="14" text-anchor="middle" fill="currentColor">3</text>
<text x="110" y="130" font-size="10" text-anchor="middle" fill="currentColor">[1]</text>
<circle cx="290" cy="100" r="17" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/><text x="290" y="105" font-size="14" text-anchor="middle" fill="currentColor">2</text>
<text x="290" y="130" font-size="10" text-anchor="middle" fill="currentColor">[2]</text>
<circle cx="60" cy="160" r="17" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/><text x="60" y="165" font-size="14" text-anchor="middle" fill="currentColor">4</text>
<text x="60" y="190" font-size="10" text-anchor="middle" fill="currentColor">[3]</text>
<circle cx="160" cy="160" r="17" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/><text x="160" y="165" font-size="14" text-anchor="middle" fill="currentColor">8</text>
<text x="160" y="190" font-size="10" text-anchor="middle" fill="currentColor">[4]</text>
<circle cx="240" cy="160" r="17" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/><text x="240" y="165" font-size="14" text-anchor="middle" fill="currentColor">7</text>
<text x="240" y="190" font-size="10" text-anchor="middle" fill="currentColor">[5]</text>
<circle cx="340" cy="160" r="17" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/><text x="340" y="165" font-size="14" text-anchor="middle" fill="currentColor">6</text>
<text x="340" y="190" font-size="10" text-anchor="middle" fill="currentColor">[6]</text>
<circle cx="35" cy="220" r="17" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/><text x="35" y="225" font-size="14" text-anchor="middle" fill="currentColor">9</text>
<text x="35" y="250" font-size="10" text-anchor="middle" fill="currentColor">[7]</text>
<circle cx="85" cy="220" r="17" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/><text x="85" y="225" font-size="14" text-anchor="middle" fill="currentColor">5</text>
<text x="85" y="250" font-size="10" text-anchor="middle" fill="currentColor">[8]</text>
<rect x="440" y="110" width="36" height="34" rx="0" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/>
<text x="458" y="132" font-size="14" text-anchor="middle" fill="currentColor">1</text>
<text x="458" y="160" font-size="11" text-anchor="middle" fill="currentColor">0</text>
<rect x="476" y="110" width="36" height="34" rx="0" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="494" y="132" font-size="14" text-anchor="middle" fill="currentColor">3</text>
<text x="494" y="160" font-size="11" text-anchor="middle" fill="currentColor">1</text>
<rect x="512" y="110" width="36" height="34" rx="0" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="530" y="132" font-size="14" text-anchor="middle" fill="currentColor">2</text>
<text x="530" y="160" font-size="11" text-anchor="middle" fill="currentColor">2</text>
<rect x="548" y="110" width="36" height="34" rx="0" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="566" y="132" font-size="14" text-anchor="middle" fill="currentColor">4</text>
<text x="566" y="160" font-size="11" text-anchor="middle" fill="currentColor">3</text>
<rect x="584" y="110" width="36" height="34" rx="0" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<text x="602" y="132" font-size="14" text-anchor="middle" fill="currentColor">8</text>
<text x="602" y="160" font-size="11" text-anchor="middle" fill="currentColor">4</text>
<rect x="620" y="110" width="36" height="34" rx="0" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<text x="638" y="132" font-size="14" text-anchor="middle" fill="currentColor">7</text>
<text x="638" y="160" font-size="11" text-anchor="middle" fill="currentColor">5</text>
<rect x="656" y="110" width="36" height="34" rx="0" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<text x="674" y="132" font-size="14" text-anchor="middle" fill="currentColor">6</text>
<text x="674" y="160" font-size="11" text-anchor="middle" fill="currentColor">6</text>
<rect x="692" y="110" width="36" height="34" rx="0" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<text x="710" y="132" font-size="14" text-anchor="middle" fill="currentColor">9</text>
<text x="710" y="160" font-size="11" text-anchor="middle" fill="currentColor">7</text>
<rect x="728" y="110" width="36" height="34" rx="0" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<text x="746" y="132" font-size="14" text-anchor="middle" fill="currentColor">5</text>
<text x="746" y="160" font-size="11" text-anchor="middle" fill="currentColor">8</text>
<text x="602" y="96" font-size="12" text-anchor="middle" fill="currentColor">the same heap as a list a[0..8]</text>
<path d="M 494 168 Q 530.0 200 566 168" fill="none" stroke="currentColor" stroke-width="1.2"/>
<polygon points="566,166 562,176 570,176" fill="currentColor"/>
<path d="M 494 168 Q 548.0 212 602 168" fill="none" stroke="currentColor" stroke-width="1.2"/>
<polygon points="602,166 598,176 606,176" fill="currentColor"/>
<text x="602" y="230" font-size="12" text-anchor="middle" fill="currentColor">children of a[i]: a[2i+1], a[2i+2]</text>
<text x="602" y="250" font-size="12" text-anchor="middle" fill="currentColor">parent of a[i]: a[(i-1)//2]</text>
</svg>
<figcaption>Figure 9.1. The min-heap that build-heap makes from [9, 4, 7, 1, 8, 2, 6, 3, 5]. The tree is stored level by level in a plain list, so no pointers are needed: the children of index i sit at 2i + 1 and 2i + 2. Every parent is at most its children.</figcaption>
</figure>

### Sift up and sift down

Every operation breaks the heap property in at most one place and then repairs it by moving one key along a path.

**Sift up** (used after insert): the key at position $i$ may be smaller than its parent. While it is, swap it with
its parent.

**Sift down** (used after extract-min): the key at position $i$ may be larger than one of its children. While it is,
swap it with the **smaller** child.

Swapping with the smaller child is what makes it correct: after the swap the new parent is the smaller child, which is
at most the other child and at most the key it replaced, so the heap property holds at the parent; the only possible
violation has moved one level down.

**Lemma 9.1 (sift down).** Suppose the subtrees of both children of $i$ are heaps. Then after sift-down at $i$, the whole
subtree of $i$ is a heap, and sift-down did at most $h_i$ swaps, where $h_i$ is the height of node $i$.

*Proof,* by induction on $h_i$. If $i$ is no larger than its children (or has none), nothing moves and the subtree is a
heap. Otherwise let $c$ be the smaller child and swap. Now position $i$ holds the old key of $c$, which is at most
everything in both subtrees (it was the smaller of the two subtree minimums), so the heap property holds at $i$. The
subtree of the other child is unchanged. The subtree of $c$ has heaps below $c$ and a possibly too-large key at $c$:
exactly the situation of the lemma, at height $h_i - 1$, so by induction one more sift-down at $c$ finishes it with at
most $h_i - 1$ more swaps. $\square$

Sift up has the mirror-image lemma: if the array is a heap except that position $i$ may be smaller than its parent,
sift-up at $i$ restores the heap with at most depth$(i)$ swaps. (When $i$ moves up past its parent $p$, the old key of
$p$ moves down to $i$'s place; it was at most everything below it already, so nothing below breaks.)

### The operations

- **find-min**: return `a[0]`. $O(1)$.
- **insert**: append the key at the end (the next free spot of the bottom level, which keeps the shape complete),
  then sift it up. $O(\log n)$.
- **extract-min**: save `a[0]`; move the last key into position 0 and shrink the list by one (the shape stays
  complete); then sift down from 0. $O(\log n)$.

Here are six pushes and six pops by hand (the program below prints the same lines):

| Operation | List after | What moved |
| --- | --- | --- |
| push 5 | [5] | |
| push 3 | [3, 5] | 3 smaller than parent 5: swap |
| push 8 | [3, 5, 8] | 8 is not smaller than 3 |
| push 1 | [1, 3, 8, 5] | 1 at position 3: swap with 5, then with 3 |
| push 9 | [1, 3, 8, 5, 9] | |
| push 2 | [1, 3, 2, 5, 9, 8] | 2 at position 5: swap with 8; not smaller than 1 |
| pop → 1 | [2, 3, 8, 5, 9] | last key 8 to the root, swaps with the smaller child 2 |
| pop → 2 | [3, 5, 8, 9] | 9 to the root, swaps with 3, then with 5 |

The pops come out in increasing order, which is the next section's sort.

### Build-heap in linear time

To turn an arbitrary list of $n$ keys into a heap, we could push them one by one: $O(n\log n)$. Robert Floyd found
something better in 1964: **sift down every internal node, from the last one back to the root.**

```python
for i in reversed(range(n // 2)):   # positions n//2 .. n-1 are leaves
    sift_down(a, i)
```

**Correctness.** Positions $\lfloor n/2\rfloor$ to $n-1$ have no children (the left child of $\lfloor n/2\rfloor$ would
be at $2\lfloor n/2\rfloor + 1 \ge n$), so each is a one-node heap. When the loop reaches $i$, both children of $i$ have
larger positions, so they have already been processed and their subtrees are heaps. By Lemma 9.1, after sift-down at
$i$ the subtree of $i$ is a heap. At the end, $i = 0$ and the whole list is a heap.

Trace on `[9, 4, 7, 1, 8, 2, 6, 3, 5]` ($n = 9$, internal positions 3, 2, 1, 0):

| Sift down at | Key | What happens | List after |
| --- | --- | --- | --- |
| 3 | 1 | children 3 and 5: already smaller | [9, 4, 7, 1, 8, 2, 6, 3, 5] |
| 2 | 7 | smaller child is 2: swap | [9, 4, 2, 1, 8, 7, 6, 3, 5] |
| 1 | 4 | smaller child 1: swap; then children 3, 5: swap with 3 | [9, 1, 2, 3, 8, 7, 6, 4, 5] |
| 0 | 9 | swap with 1, then with 3, then with 4 | [1, 3, 2, 4, 8, 7, 6, 9, 5] |

That is Figure 9.1.

**Theorem 9.2.** Build-heap runs in $O(n)$ time.

*Proof.* A sift-down at a node of height $h$ costs $O(h)$ (Lemma 9.1). Count nodes by height: in a complete binary tree
with $n$ nodes there are at most $\lceil n/2^{h+1}\rceil$ nodes of height $h$. (Half the nodes, rounding up, are
leaves; removing the leaves leaves a complete tree with $\lfloor n/2\rfloor$ nodes whose leaves are the old height-1
nodes; and so on.) So the total work is at most a constant times

$$
\sum_{h=0}^{\lfloor\log_2 n\rfloor}\left\lceil\frac{n}{2^{h+1}}\right\rceil h \;\le\; \sum_{h\ge 0}\left(\frac{n}{2^{h+1}} + 1\right)h \;\le\; \frac n2\sum_{h\ge0}\frac{h}{2^h} + \log_2^2 n .
$$

The series $\sum_{h\ge0} h x^h$ equals $x/(1-x)^2$ for $|x| < 1$ (differentiate the geometric series
$\sum x^h = 1/(1-x)$ and multiply by $x$), so with $x = \frac12$ it is $2$. The total is at most $n + \log_2^2 n = O(n)$.
$\square$

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 780 276" role="img" aria-label="A complete binary tree with 15 nodes in four rows. Row labels on the left give the height: 3, 2, 1, 0. Labels on the right: 1 node times 3 steps, 2 nodes times 2 steps, 4 nodes times 1 step, 8 leaves times 0 steps.">
<line x1="340.0" y1="40" x2="210.0" y2="95" stroke="currentColor" stroke-width="1"/>
<line x1="340.0" y1="40" x2="470.0" y2="95" stroke="currentColor" stroke-width="1"/>
<line x1="210.0" y1="95" x2="145.0" y2="150" stroke="currentColor" stroke-width="1"/>
<line x1="210.0" y1="95" x2="275.0" y2="150" stroke="currentColor" stroke-width="1"/>
<line x1="470.0" y1="95" x2="405.0" y2="150" stroke="currentColor" stroke-width="1"/>
<line x1="470.0" y1="95" x2="535.0" y2="150" stroke="currentColor" stroke-width="1"/>
<line x1="145.0" y1="150" x2="112.5" y2="205" stroke="currentColor" stroke-width="1"/>
<line x1="145.0" y1="150" x2="177.5" y2="205" stroke="currentColor" stroke-width="1"/>
<line x1="275.0" y1="150" x2="242.5" y2="205" stroke="currentColor" stroke-width="1"/>
<line x1="275.0" y1="150" x2="307.5" y2="205" stroke="currentColor" stroke-width="1"/>
<line x1="405.0" y1="150" x2="372.5" y2="205" stroke="currentColor" stroke-width="1"/>
<line x1="405.0" y1="150" x2="437.5" y2="205" stroke="currentColor" stroke-width="1"/>
<line x1="535.0" y1="150" x2="502.5" y2="205" stroke="currentColor" stroke-width="1"/>
<line x1="535.0" y1="150" x2="567.5" y2="205" stroke="currentColor" stroke-width="1"/>
<circle cx="340.0" cy="40" r="11" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/>
<text x="10" y="45" font-size="12" text-anchor="start" fill="currentColor">height 3</text>
<text x="620" y="45" font-size="12" text-anchor="start" fill="currentColor">1 node x 3 steps</text>
<circle cx="210.0" cy="95" r="11" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<circle cx="470.0" cy="95" r="11" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="10" y="100" font-size="12" text-anchor="start" fill="currentColor">height 2</text>
<text x="620" y="100" font-size="12" text-anchor="start" fill="currentColor">2 nodes x 2 steps</text>
<circle cx="145.0" cy="150" r="11" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<circle cx="275.0" cy="150" r="11" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<circle cx="405.0" cy="150" r="11" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<circle cx="535.0" cy="150" r="11" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="10" y="155" font-size="12" text-anchor="start" fill="currentColor">height 1</text>
<text x="620" y="155" font-size="12" text-anchor="start" fill="currentColor">4 nodes x 1 step</text>
<circle cx="112.5" cy="205" r="11" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<circle cx="177.5" cy="205" r="11" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<circle cx="242.5" cy="205" r="11" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<circle cx="307.5" cy="205" r="11" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<circle cx="372.5" cy="205" r="11" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<circle cx="437.5" cy="205" r="11" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<circle cx="502.5" cy="205" r="11" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<circle cx="567.5" cy="205" r="11" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<text x="10" y="210" font-size="12" text-anchor="start" fill="currentColor">height 0</text>
<text x="620" y="210" font-size="12" text-anchor="start" fill="currentColor">8 leaves x 0 steps</text>
<text x="390" y="262" font-size="12" text-anchor="middle" fill="currentColor">total work: sum of n/2^(h+1) nodes times h steps, which is at most n</text>
</svg>
<figcaption>Figure 9.2. Why build-heap is linear. A node at height h sinks at most h levels, and most nodes are near the bottom where h is small: half the nodes are leaves and never move. Here the worst total is 3 + 4 + 4 + 0 = 11 sift steps for 15 nodes.</figcaption>
</figure>

The intuition is in Figure 9.2: pushing one at a time makes the *many* nodes near the bottom potentially climb the
*whole* height, while build-heap makes only the *few* nodes near the top travel far. Each sift-down step costs at most
2 comparisons (find the smaller child, then compare with it), so build-heap uses at most about $2n$ comparisons. The
program counts them.

```python
--8<-- "books/algorithms/ch09_binary_heap.py"
```

```
push 5: [5]
push 3: [3, 5]
push 8: [3, 5, 8]
push 1: [1, 3, 8, 5]
push 9: [1, 3, 8, 5, 9]
push 2: [1, 3, 2, 5, 9, 8]
pop -> 1: [2, 3, 8, 5, 9]
pop -> 2: [3, 5, 8, 9]
pop -> 3: [5, 9, 8]
pop -> 5: [8, 9]
pop -> 8: [9]
pop -> 9: []
build-heap of [9, 4, 7, 1, 8, 2, 6, 3, 5] -> [1, 3, 2, 4, 8, 7, 6, 9, 5]
     n   build: comparisons  per n   n pushes: comparisons  per n
  1000                 1875   1.88                   2261   2.26
 10000                18832   1.88                  22669   2.27
100000               188306   1.88                 228086   2.28
n pushes of decreasing keys, n = 100000: 14.69 comparisons per push, log2 n = 16.61
pops agree with heapq: True
```

Build-heap used 1.88 comparisons per key, as the theorem predicts. Notice also that $n$ pushes of keys in *random*
order cost only about 2.3 comparisons each, not $\log_2 n$: a random new key usually belongs near the bottom, because
most of the heap is near the bottom. Pushing keys in decreasing order is the worst case: each new key climbs to the
root, and the total, $\sum_{i=1}^{n}\lfloor\log_2 i\rfloor$, is $\Theta(n\log n)$.

Python's `heapq` module is exactly this structure on a plain list (with a few speed tricks), and the last line checks
our pops against it. The [binary heap reference page](../../data-structures/binary-heap.md) has the same code in Java
and C++ with an animation.

**History.** J. W. J. Williams published the binary heap and heapsort in 1964 as "Algorithm 232: Heapsort" in
*Communications of the ACM*; the same year Robert Floyd published "Algorithm 245: Treesort 3", which builds the heap
bottom-up in linear time. The word "heap" for this structure comes from Williams's paper; it has nothing to do with
the "heap" of memory that a program allocates from.

<figure class="play" data-play="heapsift"><span class="ai-tag">AI-created</span><figcaption>Try it: ten made-up keys go into a min-heap one by one. Each lands in the next free slot and sifts up; the tree and the array are the same heap.</figcaption></figure>

## 9.3 Heapsort revisited; d-ary heaps

### Heapsort

[Chapter 5](05-Sorting-by-Comparison.md) named heapsort; now we can build it. Use a **max**-heap. Build it in place in
$O(n)$. Then repeat: swap the root (the largest key) with the last key of the heap, shrink the heap by one (the largest
key is now in its final place, just after the heap), and sift down the new root.

```python
def heapsort(a):
    n = len(a)
    for i in reversed(range(n // 2)):
        sift_down(a, i, n)              # max-heap on a[0:n]
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]     # largest to its place
        sift_down(a, 0, end)            # heap is now a[0:end]
```

**Invariant:** before each pass of the second loop, `a[0:end+1]` is a max-heap holding the `end+1` smallest keys, and
`a[end+1:]` holds the largest keys in sorted order. The swap moves the largest heap key to the front of the sorted part
and the sift-down restores the heap, so the invariant holds again with `end` one smaller. At the end the whole list is
sorted.

**Cost:** $O(n)$ to build, plus $n-1$ sift-downs of $O(\log n)$ each: $O(n\log n)$ in the worst case, with $O(1)$ extra
memory. It is the only one of the classic $O(n\log n)$ sorts that has both properties (merge sort needs $O(n)$ extra
memory; quicksort can be quadratic). It is not **stable** (equal keys can change order), and it jumps around the array,
so it uses the processor's cache badly; that is why libraries prefer quicksort and fall back to heapsort only to cap
the worst case (introsort, [Chapter 5](05-Sorting-by-Comparison.md)).

The program traces heapsort on `[4, 10, 3, 5, 1, 8]`; the bar `|` separates the heap from the sorted tail.

### d-ary heaps

Why must each node have two children? A **$d$-ary heap** gives each node $d$ children: the children of $i$ are
$di+1, \dots, di+d$ and the parent of $i$ is $\lfloor(i-1)/d\rfloor$ (the same counting argument as before). The height
is about $\log_d n$, so

- **sift-up** (insert, decrease-key) costs $O(\log_d n)$: one comparison per level;
- **sift-down** (extract-min) costs $O(d\log_d n)$: at each level, find the smallest of $d$ children.

Larger $d$ makes inserts and decrease-keys cheaper and extract-mins dearer. That is exactly the trade Dijkstra's
algorithm wants on a graph with $n$ vertices and $m$ edges: it does up to $m$ decrease-keys but only $n$ extract-mins,
for a total of $O(m\log_d n + nd\log_d n)$. Choosing $d \approx \max(2, m/n)$ gives $O(m\log_{m/n} n)$, which is
$O(m)$ when the graph is dense ($m \ge n^{1+\varepsilon}$). Donald Johnson analysed this choice in 1975. A 4-ary heap is
also often faster than a binary heap even on ordinary workloads, because its four children usually sit in one cache
line.

```python
--8<-- "books/algorithms/ch09_heapsort_dary.py"
```

```
max-heap   : [10, 5, 8, 4, 1, 3]
after 1 out: [8, 5, 3, 4, 1] | [10]
after 2 out: [5, 4, 3, 1] | [8, 10]
after 3 out: [4, 1, 3] | [5, 8, 10]
after 4 out: [3, 1] | [4, 5, 8, 10]
after 5 out: [1] | [3, 4, 5, 8, 10]
sorted     : [1, 3, 4, 5, 8, 10]
heapsort d = 2: 28.2 comparisons per item
heapsort d = 3: 27.2 comparisons per item
heapsort d = 4: 28.9 comparisons per item
d   push comparisons   pop comparisons   (per operation, n = 50000)
 2              13.69             25.88
 4               7.42             27.17
 8               5.14             36.65
16               3.91             54.01
```

The table shows the trade: going from $d = 2$ to $d = 16$ cuts the cost of a worst-case push from 13.7 to 3.9
comparisons and raises a pop from 25.9 to 54.0.

## 9.4 Decrease-key and indexed heaps

*Level: intermediate.*

Dijkstra's shortest-path algorithm ([Chapter 16](16-Shortest-Paths.md); [reference page](../../graphs/dijkstra.md))
keeps every unfinished vertex in a priority queue, keyed by the best distance found so far. When it finds a shorter
path to vertex $v$, it must **decrease $v$'s key**. Prim's minimum-spanning-tree algorithm
([Chapter 17](17-Spanning-Trees-Flows-and-Matching.md)) does the same. The heap can lower a key easily (lowering a key
can only break the heap property with its parent, so sift up), but first it must **find** $v$ in the array, and a heap
has no way to search.

The fix is an **indexed heap** (also called an addressable heap): name items $0, \dots, n-1$, store item names in the
heap array, and keep a second array `pos` with `pos[item]` = the item's current index in the heap. Every swap updates
`pos` for both items. Then:

- **decrease-key(item, p)**: set its priority to $p$, then sift up from `pos[item]`. $O(\log n)$.
- **contains(item)**: `pos[item] != -1`. $O(1)$.
- **delete(item)**: swap it with the last entry, remove it, then sift the moved entry up or down, whichever is
  needed. $O(\log n)$.

**Invariant:** for every item in the heap, `heap[pos[item]] == item`. It holds after each operation because every
change of `heap` goes through one `_swap` function that updates `pos` for the two entries it moves, and push and pop
set `pos` for the item they add or remove.

The program builds an indexed heap of five items, lowers item 4 from 60 to 10, and shows that `pos` follows it to the
root. Then it runs Dijkstra on the small road map of Figure 9.5 and on a random graph.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 620 230" role="img" aria-label="A graph of six places numbered 0 to 5. Edges with lengths: 0-1 is 7, 0-2 is 9, 0-5 is 14, 1-2 is 10, 1-3 is 15, 2-3 is 11, 2-5 is 2, 3-4 is 6, 4-5 is 9. Each node shows its shortest distance from 0: 0, 7, 9, 20, 20, 11.">
<line x1="60" y1="120" x2="190" y2="40" stroke="currentColor" stroke-width="1.5"/>
<line x1="60" y1="120" x2="210" y2="130" stroke="currentColor" stroke-width="1.5"/>
<line x1="60" y1="120" x2="190" y2="200" stroke="currentColor" stroke-width="1.5"/>
<line x1="190" y1="40" x2="210" y2="130" stroke="currentColor" stroke-width="1.5"/>
<line x1="190" y1="40" x2="380" y2="60" stroke="currentColor" stroke-width="1.5"/>
<line x1="210" y1="130" x2="380" y2="60" stroke="currentColor" stroke-width="1.5"/>
<line x1="210" y1="130" x2="190" y2="200" stroke="currentColor" stroke-width="1.5"/>
<line x1="380" y1="60" x2="400" y2="190" stroke="currentColor" stroke-width="1.5"/>
<line x1="400" y1="190" x2="190" y2="200" stroke="currentColor" stroke-width="1.5"/>
<text x="118" y="72" font-size="12" text-anchor="middle" fill="currentColor">7</text>
<text x="135" y="118" font-size="12" text-anchor="middle" fill="currentColor">9</text>
<text x="115" y="176" font-size="12" text-anchor="middle" fill="currentColor">14</text>
<text x="210" y="88" font-size="12" text-anchor="middle" fill="currentColor">10</text>
<text x="285" y="42" font-size="12" text-anchor="middle" fill="currentColor">15</text>
<text x="300" y="106" font-size="12" text-anchor="middle" fill="currentColor">11</text>
<text x="210" y="170" font-size="12" text-anchor="middle" fill="currentColor">2</text>
<text x="402" y="128" font-size="12" text-anchor="middle" fill="currentColor">6</text>
<text x="295" y="210" font-size="12" text-anchor="middle" fill="currentColor">9</text>
<circle cx="60" cy="120" r="17" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/>
<text x="60" y="125" font-size="14" text-anchor="middle" fill="currentColor">0</text>
<circle cx="190" cy="40" r="17" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="190" y="45" font-size="14" text-anchor="middle" fill="currentColor">1</text>
<circle cx="210" cy="130" r="17" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="210" y="135" font-size="14" text-anchor="middle" fill="currentColor">2</text>
<circle cx="380" cy="60" r="17" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="380" y="65" font-size="14" text-anchor="middle" fill="currentColor">3</text>
<circle cx="400" cy="190" r="17" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="400" y="195" font-size="14" text-anchor="middle" fill="currentColor">4</text>
<circle cx="190" cy="200" r="17" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<text x="190" y="205" font-size="14" text-anchor="middle" fill="currentColor">5</text>
<text x="470" y="40" font-size="12" text-anchor="start" fill="currentColor">distance from 0:</text>
<text x="470" y="62" font-size="12" text-anchor="start" fill="currentColor">0: 0    1: 7</text>
<text x="470" y="82" font-size="12" text-anchor="start" fill="currentColor">2: 9    3: 20</text>
<text x="470" y="102" font-size="12" text-anchor="start" fill="currentColor">4: 20   5: 11</text>
<text x="470" y="140" font-size="12" text-anchor="start" fill="currentColor">5 starts at 14 and is</text>
<text x="470" y="158" font-size="12" text-anchor="start" fill="currentColor">decreased to 11 when 2</text>
<text x="470" y="176" font-size="12" text-anchor="start" fill="currentColor">is finished (9 + 2)</text>
</svg>
<figcaption>Figure 9.5. The small road map used by the program. When Dijkstra's algorithm finishes place 2 at distance 9, it lowers place 5's key from 14 to 11 and place 3's key from 22 to 20: two decrease-key operations.</figcaption>
</figure>

```python
--8<-- "books/algorithms/ch09_indexed_heap.py"
```

```
heap of items: [3, 1, 2, 0, 4]  positions: [3, 1, 2, 0, 4]
after decrease_key(4, 10): [4, 3, 2, 0, 1]  positions: [3, 4, 2, 1, 0]
pops: [(4, 10), (3, 20), (1, 30), (2, 40), (0, 50)]
distances from 0: [0, 7, 9, 20, 20, 11]
same distances: True
indexed heap: {'push': 19999, 'decrease': 19166, 'pop': 19999}
heapq, lazy  : {'push': 39177, 'stale': 19178, 'pop': 39177, 'max size': 24767}
```

### Lazy deletion: the trick when there is no decrease-key

Python's `heapq` has no decrease-key. The standard trick is to **push a new entry** `(new_distance, v)` and leave the
old one in the heap. When an entry is popped, compare it with the best known distance; if it is larger, it is
**stale** (out of date): skip it. Correctness is simple: the first time $v$ is popped, it is popped with its smallest
key, because all its entries are in the heap and the smallest comes out first; later entries for $v$ are stale.

The cost: the heap can hold up to $m$ entries instead of $n$, so each operation costs $O(\log m)$; but
$m \le n^2$ means $\log m \le 2\log n$, so the total is still $O((n+m)\log n)$. In the output, the lazy version pushed
about twice as many entries, and 19,178 of its pops were stale; but `heapq` is written in C, and in practice the lazy
version is usually the faster one in Python. That is the honest lesson of this whole chapter: **asymptotically better
is not the same as faster**.

## 9.5 Mergeable heaps: leftist and binomial heaps

*Level: advanced.*

Suppose two print servers each keep a priority queue of jobs, and one server goes down: its queue must be **merged**
into the other. With binary heaps the only way is to concatenate the arrays and run build-heap: $O(n)$. Can we meld in
$O(\log n)$? Not with an array, because the merged array must be complete. We go back to pointers.

### Leftist heaps

Clark Crane introduced **leftist heaps** in his 1972 Stanford thesis, and Knuth popularised them in *The Art of
Computer Programming*, vol. 3. The idea: if merging is done along a short path, it is fast. So make one path
guaranteed short.

For a node $x$ in a binary tree, let $s(x)$, the **null-path length**, be the length of the shortest path from $x$
down to an empty child slot, counted in nodes: $s(\text{empty}) = 0$ and $s(x) = 1 + \min(s(x.\text{left}), s(x.\text{right}))$.
A **leftist heap** is a heap-ordered binary tree in which, at every node, $s(\text{left}) \ge s(\text{right})$. So the
shortest way down is always to go right, and $s(x) = 1 + s(x.\text{right})$: the **right spine** (the path from the
root always going right) is a shortest path.

**Lemma 9.3.** A leftist heap with $n$ nodes has a right spine of at most $\log_2(n+1)$ nodes.

*Proof.* If the right spine has $r$ nodes, then $s(\text{root}) = r$, so every path from the root to an empty slot
has at least $r$ nodes, which means the top $r$ levels are completely full: at least $2^r - 1$ nodes. So
$n \ge 2^r - 1$. $\square$

**Merge** two leftist heaps $a$ and $b$: let $a$ be the one with the smaller root. Recursively merge $b$ into $a$'s
right subtree. Then, if the left child's $s$ is now smaller than the right child's, swap the children, and recompute
$s(a)$.

```python
def lmerge(a, b):
    if a is None: return b
    if b is None: return a
    if b.key < a.key: a, b = b, a
    a.right = lmerge(a.right, b)
    if s(a.left) < s(a.right):
        a.left, a.right = a.right, a.left
    a.s = s(a.right) + 1
    return a
```

**Correctness:** the smaller root stays on top, so heap order holds; the swap restores the leftist rule at every node
on the path. **Cost:** every recursive call moves one step down the right spine of $a$ or of $b$, so there are at most
$r_a + r_b \le 2\log_2(n+1)$ calls: $O(\log n)$. **Insert** is a merge with a one-node heap; **extract-min** removes the
root and merges its two subtrees. Both are $O(\log n)$. The program merges two small leftist heaps and pops the result
in order.

A simpler relative, the **skew heap** (Sleator and Tarjan 1986), drops $s$ entirely and *always* swaps the children
after merging. Its right spine can be long, but its amortized cost is $O(\log n)$, proved by a potential argument like
the splay tree's.

### Binomial heaps

Jean Vuillemin's **binomial heap** (1978, "A data structure for manipulating priority queues") takes a different
route: it is not one tree but a *list* of trees, of very particular shapes.

The **binomial tree** $B_k$ is defined by: $B_0$ is a single node; $B_k$ is two copies of $B_{k-1}$, with the root of
one made the leftmost child of the root of the other.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 760 240" role="img" aria-label="Binomial trees B0 to B3. B0 is one node. B1 is a root with one child. B2 is a root whose children are a B1 and a B0. B3 is a root whose children are a B2, a B1 and a B0. They have 1, 2, 4 and 8 nodes.">
<circle cx="40" cy="40" r="9" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<text x="40" y="22" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">B0</text>
<text x="40" y="225" font-size="12" text-anchor="middle" fill="currentColor">1 node</text>
<line x1="100" y1="40" x2="100" y2="80" stroke="currentColor" stroke-width="1.2"/>
<circle cx="100" cy="80" r="9" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<circle cx="100" cy="40" r="9" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="100" y="22" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">B1</text>
<text x="113" y="225" font-size="12" text-anchor="middle" fill="currentColor">2 nodes</text>
<line x1="190" y1="40" x2="190" y2="80" stroke="currentColor" stroke-width="1.2"/>
<line x1="190" y1="80" x2="190" y2="120" stroke="currentColor" stroke-width="1.2"/>
<circle cx="190" cy="120" r="9" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<circle cx="190" cy="80" r="9" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<line x1="190" y1="40" x2="242" y2="80" stroke="currentColor" stroke-width="1.2"/>
<circle cx="242" cy="80" r="9" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<circle cx="190" cy="40" r="9" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="190" y="22" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">B2</text>
<text x="229" y="225" font-size="12" text-anchor="middle" fill="currentColor">4 nodes</text>
<line x1="340" y1="40" x2="340" y2="80" stroke="currentColor" stroke-width="1.2"/>
<line x1="340" y1="80" x2="340" y2="120" stroke="currentColor" stroke-width="1.2"/>
<line x1="340" y1="120" x2="340" y2="160" stroke="currentColor" stroke-width="1.2"/>
<circle cx="340" cy="160" r="9" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<circle cx="340" cy="120" r="9" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<line x1="340" y1="80" x2="392" y2="120" stroke="currentColor" stroke-width="1.2"/>
<circle cx="392" cy="120" r="9" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<circle cx="340" cy="80" r="9" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<line x1="340" y1="40" x2="444" y2="80" stroke="currentColor" stroke-width="1.2"/>
<line x1="444" y1="80" x2="444" y2="120" stroke="currentColor" stroke-width="1.2"/>
<circle cx="444" cy="120" r="9" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<circle cx="444" cy="80" r="9" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<line x1="340" y1="40" x2="496" y2="80" stroke="currentColor" stroke-width="1.2"/>
<circle cx="496" cy="80" r="9" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<circle cx="340" cy="40" r="9" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="340" y="22" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">B3</text>
<text x="431" y="225" font-size="12" text-anchor="middle" fill="currentColor">8 nodes</text>
<text x="560" y="150" font-size="12" text-anchor="start" fill="currentColor">B3 = two B2 trees linked:</text>
<text x="560" y="168" font-size="12" text-anchor="start" fill="currentColor">the larger root goes under</text>
<text x="560" y="186" font-size="12" text-anchor="start" fill="currentColor">the smaller one</text>
</svg>
<figcaption>Figure 9.3. Binomial trees. B<sub>k</sub> is a root whose children are B<sub>k-1</sub>, ..., B<sub>1</sub>, B<sub>0</sub>; equivalently, two copies of B<sub>k-1</sub> with one root hung under the other. B<sub>k</sub> has 2<sup>k</sup> nodes, height k, and its root has degree k.</figcaption>
</figure>

Properties of $B_k$, each by induction on $k$ from the definition:

1. it has $2^k$ nodes (two copies of $2^{k-1}$);
2. its height is $k$ (one more than $B_{k-1}$);
3. its root has degree $k$, and the root's children are roots of $B_{k-1}, B_{k-2}, \dots, B_0$;
4. it has exactly $\binom{k}{d}$ nodes at depth $d$. This gives the name. The nodes of $B_k$ at depth $d$ are the
   nodes of the first copy at depth $d$ plus the nodes of the second copy at depth $d - 1$, so the count is
   $\binom{k-1}{d} + \binom{k-1}{d-1} = \binom{k}{d}$, Pascal's rule.

A **binomial heap** is a set of heap-ordered binomial trees, **at most one of each order $k$**. Since $B_k$ has $2^k$
nodes, a heap of $n$ keys has one tree $B_k$ exactly for each 1-bit in the binary expansion of $n$. A heap of 13 keys
($13 = 1101_2$) consists of $B_0$, $B_2$ and $B_3$, with 1, 4 and 8 keys. So there are at most
$\lfloor\log_2 n\rfloor + 1$ trees, and find-min looks at their roots in $O(\log n)$ (or keeps a pointer to the
smallest).

**Merge is binary addition.** Go through the orders $k = 0, 1, 2, \dots$. If only one of the two heaps (plus a possible
"carry") has a $B_k$, keep it. If two trees of order $k$ meet, **link** them: the one with the larger root becomes the
leftmost child of the other, giving a $B_{k+1}$, which is carried to the next order. This is exactly adding two binary
numbers with carries, and it costs $O(1)$ per order, so $O(\log n)$. The program merges a heap of 13 keys and one of
11 keys; $1101_2 + 1011_2 = 11000_2 = 24$, and the result is $B_3$ and $B_4$.

- **Insert**: merge with a one-node heap ($B_0$). Like incrementing a binary counter, this costs $O(\log n)$ in the
  worst case but **$O(1)$ amortized**: the classic binary-counter example of amortized analysis (CLRS, section 16.1)
  applies word for word, with links in place of bit flips.
- **Extract-min**: find the tree whose root is smallest, remove it, and note that its children $B_{k-1}, \dots, B_0$
  form a binomial heap by themselves (property 3). Merge them back in. $O(\log n)$.
- **Decrease-key**: sift up within the tree, $O(\log n)$ since the height is at most $\log_2 n$.

```python
--8<-- "books/algorithms/ch09_mergeable.py"
```

```
leftist A: 3(8(21,14),10(17,.))
leftist B: 6(7(18,24),12(37,18(33,.)))
merged   : 3(6(7(18,24),10(12(37,18(33,.)),17)),8(21,14))
pops     : [3, 6, 7, 8, 10, 12, 14, 17, 18, 18, 21, 24, 33, 37]
binomial heap of 13 keys: B0 B2 B3  sizes: [1, 4, 8]
binomial heap of 11 keys: B0 B1 B3
after merging (24 = 11000): B3 B4
n = 100000: leftist right spine 12 nodes; binomial heap has 6 trees (bits of 100000 = 6)
1000 pops agree and are sorted: True
```

The leftist heap of 100,000 random keys has a right spine of 12 nodes, under the bound $\log_2(100001) \approx 16.6$;
the binomial heap has 6 trees, one for each 1-bit of $100000 = 11000011010100000_2$.

## 9.6 Fibonacci heaps and pairing heaps

*Level: expert.*

In Dijkstra's algorithm on a graph with $n$ vertices and $m$ edges there are $n$ inserts, $n$ extract-mins and up to
$m$ decrease-keys. With a binary heap that is $O((n + m)\log n)$. For dense graphs, $m$ can be near $n^2$, and the
decrease-keys dominate. If decrease-key cost $O(1)$, Dijkstra would run in $O(m + n\log n)$. In 1984 Michael Fredman
and Robert Tarjan built a heap that does exactly that ("Fibonacci heaps and their uses in improved network optimization
algorithms", FOCS 1984; *Journal of the ACM* 1987):

| Operation | binary heap (worst) | binomial heap | Fibonacci heap (amortized) |
| --- | --- | --- | --- |
| insert | $O(\log n)$ | $O(1)$ amortized | $O(1)$ |
| find-min | $O(1)$ | $O(1)$ with a pointer | $O(1)$ |
| meld | $O(n)$ | $O(\log n)$ | $O(1)$ |
| decrease-key | $O(\log n)$ | $O(\log n)$ | $O(1)$ |
| extract-min | $O(\log n)$ | $O(\log n)$ | $O(\log n)$ |

Remember from 9.1 that insert and extract-min cannot both be $o(\log n)$; the Fibonacci heap puts all the
$\log n$ into extract-min.

### The structure

A Fibonacci heap is a collection of heap-ordered trees, like a binomial heap, but **lazy**: the trees can have any
shape, and nothing is tidied until an extract-min forces it. The roots are kept in a circular doubly linked list (so
two lists can be spliced together in $O(1)$), with a pointer to the minimum root. Each node keeps its **degree**
(number of children) and a **mark** bit.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 780 245" role="img" aria-label="A Fibonacci heap with four roots, 9, 4, 12 and 6, joined in a circular doubly linked list, and a min pointer to 4. Root 4 has children 8 and 11; 8 has child 15. Root 6 has children 7 and 13; 7 has child 10. Nodes 8 and 13 are marked.">
<line x1="98" y1="66" x2="183.0" y2="66.0" stroke="currentColor" stroke-width="1.1"/><polygon points="192,66 183.0,70.0 183.0,62.0" fill="currentColor"/>
<line x1="192" y1="74" x2="107.0" y2="74.0" stroke="currentColor" stroke-width="1.1"/><polygon points="98,74 107.0,70.0 107.0,78.0" fill="currentColor"/>
<line x1="228" y1="66" x2="323.0" y2="66.0" stroke="currentColor" stroke-width="1.1"/><polygon points="332,66 323.0,70.0 323.0,62.0" fill="currentColor"/>
<line x1="332" y1="74" x2="237.0" y2="74.0" stroke="currentColor" stroke-width="1.1"/><polygon points="228,74 237.0,70.0 237.0,78.0" fill="currentColor"/>
<line x1="368" y1="66" x2="453.0" y2="66.0" stroke="currentColor" stroke-width="1.1"/><polygon points="462,66 453.0,70.0 453.0,62.0" fill="currentColor"/>
<line x1="462" y1="74" x2="377.0" y2="74.0" stroke="currentColor" stroke-width="1.1"/><polygon points="368,74 377.0,70.0 377.0,78.0" fill="currentColor"/>
<path d="M 498 70 Q 560 70 560 30 L 60 30 Q 40 30 40 50 L 40 62" fill="none" stroke="currentColor" stroke-width="1" stroke-dasharray="4 3"/>
<polygon points="40,70 36,60 44,60" fill="currentColor"/>
<text x="300" y="24" font-size="11" text-anchor="middle" fill="currentColor">root list (circular, doubly linked)</text>
<line x1="210" y1="70" x2="170" y2="140" stroke="currentColor" stroke-width="1.5"/>
<line x1="210" y1="70" x2="250" y2="140" stroke="currentColor" stroke-width="1.5"/>
<line x1="170" y1="140" x2="170" y2="210" stroke="currentColor" stroke-width="1.5"/>
<line x1="480" y1="70" x2="440" y2="140" stroke="currentColor" stroke-width="1.5"/>
<line x1="480" y1="70" x2="520" y2="140" stroke="currentColor" stroke-width="1.5"/>
<line x1="440" y1="140" x2="440" y2="210" stroke="currentColor" stroke-width="1.5"/>
<circle cx="80" cy="70" r="17" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/><text x="80" y="75" font-size="14" text-anchor="middle" fill="currentColor">9</text>
<circle cx="210" cy="70" r="17" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/><text x="210" y="75" font-size="14" text-anchor="middle" fill="currentColor">4</text>
<circle cx="350" cy="70" r="17" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/><text x="350" y="75" font-size="14" text-anchor="middle" fill="currentColor">12</text>
<circle cx="480" cy="70" r="17" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/><text x="480" y="75" font-size="14" text-anchor="middle" fill="currentColor">6</text>
<circle cx="170" cy="140" r="17" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/><text x="170" y="145" font-size="14" text-anchor="middle" fill="currentColor">8</text>
<circle cx="250" cy="140" r="17" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/><text x="250" y="145" font-size="14" text-anchor="middle" fill="currentColor">11</text>
<circle cx="170" cy="210" r="17" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/><text x="170" y="215" font-size="14" text-anchor="middle" fill="currentColor">15</text>
<circle cx="440" cy="140" r="17" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/><text x="440" y="145" font-size="14" text-anchor="middle" fill="currentColor">7</text>
<circle cx="520" cy="140" r="17" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/><text x="520" y="145" font-size="14" text-anchor="middle" fill="currentColor">13</text>
<circle cx="440" cy="210" r="17" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/><text x="440" y="215" font-size="14" text-anchor="middle" fill="currentColor">10</text>
<line x1="210" y1="118" x2="210.0" y2="99.0" stroke="currentColor" stroke-width="1.5"/><polygon points="210,90 214.0,99.0 206.0,99.0" fill="currentColor"/>
<text x="210" y="132" font-size="12" text-anchor="middle" fill="currentColor">min</text>
<rect x="600" y="60" width="14" height="14" rx="2" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<text x="620" y="72" font-size="12" text-anchor="start" fill="currentColor">the minimum</text>
<rect x="600" y="90" width="14" height="14" rx="2" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/>
<text x="620" y="102" font-size="12" text-anchor="start" fill="currentColor">marked: lost a child</text>
<rect x="600" y="120" width="14" height="14" rx="2" fill="#9cc9ea" stroke="currentColor" stroke-width="1.2"/>
<text x="620" y="132" font-size="12" text-anchor="start" fill="currentColor">unmarked</text>
<text x="600" y="180" font-size="12" text-anchor="start" fill="currentColor">t(H) = 4 trees</text>
<text x="600" y="200" font-size="12" text-anchor="start" fill="currentColor">m(H) = 2 marked</text>
<text x="600" y="220" font-size="12" text-anchor="start" fill="currentColor">potential = t + 2m = 8</text>
</svg>
<figcaption>Figure 9.4. A Fibonacci heap is a list of heap-ordered trees with a pointer to the smallest root. Pushes just add roots; the work of tidying up is put off until a pop. A marked node has already lost one child since it last became a child itself.</figcaption>
</figure>

- **insert**: add a new one-node tree to the root list; update the min pointer. $O(1)$.
- **meld**: splice the two root lists; keep the smaller min. $O(1)$.
- **extract-min**: remove the min root and add each of its children to the root list. Then **consolidate**: while two
  roots have the same degree, **link** them (the larger root becomes a child of the smaller). Use an array indexed by
  degree to find equal degrees. At the end, every root has a different degree; find the new min among them.
- **decrease-key($x$, $k$)**: lower the key. If $x$ is now smaller than its parent, **cut** $x$ from its parent and make
  it a root (unmarked). Then the **cascading cut**: if the parent was unmarked, mark it (it has lost one child) and stop;
  if it was already marked (this is its second lost child), cut it too, make it a root, and continue with its parent.
  Roots are never marked.

The marks are the clever part. Without them, decrease-key could cut so many children out of a tree that a node of high
degree had a tiny subtree, and the degree bound below would fail. The rule "a node may lose at most one child before it
is cut itself" keeps every subtree big compared to its root's degree.

### The amortized analysis

We use the **potential method** of [Chapter 4](04-Lists-Stacks-and-Queues.md): define a potential $\Phi$ of the
structure, never negative and zero at the start, and charge each operation its **amortized cost** = actual cost +
change in $\Phi$. The sum of amortized costs is then an upper bound on the sum of actual costs. For a Fibonacci heap $H$,

$$
\Phi(H) = t(H) + 2\,m(H),
$$

where $t(H)$ is the number of trees (roots) and $m(H)$ the number of marked nodes. Measure actual cost in units of
$O(1)$ work, and let $D(n)$ be the largest degree any node can have in a heap of $n$ nodes; we prove $D(n) = O(\log n)$
next.

**insert**: actual cost 1, $t$ goes up by 1: amortized cost 2, which is $O(1)$. **meld**: actual $O(1)$, and the
potential of the union is the sum of the two potentials: $O(1)$.

**extract-min**: let $t$ be the number of roots before. Adding the min's children to the root list costs at most
$D(n)$; consolidation does $O(1)$ work per root it handles, and there are at most $t + D(n)$ roots to handle (each link
removes one root, so the number of links is at most that too). Actual cost: $O(t + D(n))$. Afterwards all roots have
different degrees, each at most $D(n)$, so there are at most $D(n) + 1$ roots; marks do not increase. So

$$
\text{amortized} \le O(t + D(n)) + \big((D(n) + 1) + 2m\big) - \big(t + 2m\big) = O(D(n)),
$$

where we scale the units of potential to cover the constant hidden in the $O(t)$: the $t$ in the actual cost is paid
by the $-t$ in the potential change. That is the point of $t$ in $\Phi$: the lazy inserts each left a coin on their
root, and consolidation spends them.

**decrease-key** with $c$ cuts in all (the first cut plus $c - 1$ cascading cuts): actual cost $O(c)$. Each cut adds one
root: $t$ rises by $c$. Each cascading cut unmarks a marked node ($c - 1$ of them), and at most one node becomes newly
marked at the end. So $m$ changes by at most $-(c - 1) + 1 = 2 - c$, and

$$
\Delta\Phi \le c + 2(2 - c) = 4 - c .
$$

Amortized cost: $O(c) + 4 - c = O(1)$, again after scaling the units. This is why marks count *twice* in $\Phi$: each
marked node holds two coins, one to pay for its own cut and one for the new root it becomes.

### Why the degrees are logarithmic: the Fibonacci in the name

**Lemma 9.4.** Let $x$ be any node and let its children $y_1, y_2, \dots, y_k$ be listed in the order in which they
were linked to $x$, oldest first. Then $y_i$ has degree at least $i - 2$.

*Proof.* When $y_i$ was linked to $x$, the children $y_1, \dots, y_{i-1}$ were already there, so $x$ had degree at least
$i - 1$; nodes are linked only when their degrees are equal, so $y_i$ also had degree at least $i - 1$. Since then $y_i$
has lost at most one child (a second loss would have cut it from $x$). So its degree is at least $i - 2$. $\square$

**Lemma 9.5.** A node of degree $k$ has at least $F_{k+2} \ge \varphi^k$ nodes in its subtree, where $F$ are the
Fibonacci numbers ($F_1 = F_2 = 1$) and $\varphi = (1 + \sqrt5)/2$.

*Proof.* Let $s_k$ be the fewest nodes possible in the subtree of a degree-$k$ node. Then $s_0 = 1$, $s_1 = 2$, and
counting the node itself, its first child (at least 1 node), and children $y_2, \dots, y_k$ of degrees at least
$0, \dots, k - 2$:

$$
s_k \ge 2 + \sum_{i=2}^{k} s_{i-2} = 2 + \sum_{j=0}^{k-2} s_j .
$$

The Fibonacci numbers satisfy $F_{k+2} = 1 + \sum_{j=0}^{k} F_j$ (with $F_0 = 0$), which by induction gives
$s_k \ge F_{k+2}$. And $F_{k+2} \ge \varphi^k$ is the same induction as in Theorem 8.2 of
[Chapter 8](08-Trees-and-Balanced-Search-Trees.md). $\square$

So $n \ge \varphi^{D(n)}$, that is $D(n) \le \log_\varphi n \approx 1.44\log_2 n$, and extract-min is $O(\log n)$
amortized. Fredman and Tarjan named the heap after this lemma. The program checks it: after one extract-min on 50,000
keys the largest degree was 15, under $\log_\varphi 50000 \approx 22.5$.

**The payoff.** With a Fibonacci heap, Dijkstra's algorithm runs in $O(m + n\log n)$ and Prim's in the same bound; for
dense graphs that is $O(m)$, linear. This was the best known bound for Dijkstra in the comparison model for decades,
and it is optimal for algorithms that must output the vertices in sorted order of distance.

### Why it is rarely used in practice

The program races three versions of Dijkstra on a random graph with 30,000 vertices and 150,000 edges. On the run shown
above, the plain `heapq` version with lazy deletion was the fastest, the pairing heap second and the Fibonacci heap
the slowest, and repeated runs keep that order. The reasons are the usual ones:

- **Constants.** Each node carries a key, a parent pointer, a child list, sibling links, a degree and a mark; every
  operation chases pointers. A binary heap is one array.
- **Memory locality.** The array heap's nodes sit next to each other in memory and in the cache; the Fibonacci heap's
  are scattered.
- **Sparse graphs.** Real road networks have $m$ only a few times $n$, and then $m\log n$ and $m + n\log n$ differ by a
  small factor that the constants swallow.
- **In Python**, `heapq` runs in C and our heaps in Python, which alone is a factor of several.

Studies that implemented many heaps carefully in C or C++ have generally found binary or 4-ary heaps, or pairing heaps,
the fastest for Dijkstra on realistic graphs. Fibonacci heaps matter in **theory**: they are how the best bounds for
shortest paths, minimum spanning trees and weighted matching were first proved.

### Pairing heaps

The **pairing heap** (Fredman, Sedgewick, Sleator and Tarjan, "The pairing heap: a new form of self-adjusting heap",
*Algorithmica* 1986) is a self-adjusting heap in the spirit of the splay tree: one heap-ordered tree of any shape, with
no degrees, no marks, nothing stored but the links.

- **meld**: compare the two roots; the larger becomes the first child of the smaller. $O(1)$.
- **insert**: meld with a one-node tree. $O(1)$.
- **decrease-key**: cut the node's subtree out and meld it with the root. $O(1)$ actual.
- **extract-min**: remove the root, leaving its children as a list of trees. Meld them in **two passes**: first meld
  them in pairs from left to right, then meld the resulting trees from right to left into one.

The two-pass rule is to pairing heaps what zig-zig is to splay trees: a simple one-pass meld would also be correct but
can be slow, while the pairing roughly halves the number of trees each time. Fredman, Sedgewick, Sleator and Tarjan
proved $O(\log n)$ amortized for extract-min. The exact amortized cost of decrease-key is a long-standing open problem:
Fredman (1999) proved that it cannot be $O(1)$ in this kind of structure (it is $\Omega(\log\log n)$ for pairing heaps),
and Pettie (2005) proved an upper bound of $O(2^{2\sqrt{\log\log n}})$, which grows more slowly than any power of
$\log n$. Pairing heaps are short to write and fast in practice; the GNU C++ library's policy-based data structures
offer one, and they are often the fastest heap with decrease-key in benchmarks.

```python
--8<-- "books/algorithms/ch09_fibonacci_pairing.py"
```

```
13 pushes: roots 13 min 3
pop -> 3 | roots after consolidate: [(7, 3), (24, 2)] | links 10
decrease 46->15, 35->5: roots [5, 7, 15, 24] | min 5 | cuts 2
Fibonacci heap, n = 50000: max degree after one pop 15, bound log_phi n = 22.5
2000 pops agree after 10000 decrease-keys: True
all three agree: True
Dijkstra, n = 30000, m = 150000: heapq 0.42 s, Fibonacci 0.76 s, pairing 0.64 s
```

(Timings depend on the machine; they are from the run that produced this output.)

**The rest of the family.** Gerth Brodal (1996) built a heap with the Fibonacci bounds in the **worst case**, not just
amortized, but it is very complicated. Haeupler, Sen and Tarjan's **rank-pairing heaps** (2011) get the Fibonacci
amortized bounds with a structure closer to pairing heaps, and Brodal, Lagogiannis and Tarjan's **strict Fibonacci
heaps** (2012) get the worst-case bounds with a simpler design. For the planners that move a rover across Mars, where
the map is a sparse grid, the binary heap of 9.2 remains the honest default.

## 9.7 Which priority queue to use

| You need | Use |
| --- | --- |
| push and pop only | a binary heap (`heapq` in Python, `PriorityQueue` in Java, `std::priority_queue` in C++) |
| decrease-key, with a fixed set of items | an indexed binary or 4-ary heap |
| decrease-key, but your library has none | lazy deletion: push again, skip stale entries |
| fast merging | a leftist, skew, binomial or pairing heap |
| the best theoretical bounds, in a proof | a Fibonacci heap |
| the $k$ largest of a stream | a min-heap of size $k$ (exercise 7) |
| sorted order and successors as well | a balanced search tree ([Chapter 8](08-Trees-and-Balanced-Search-Trees.md)) |

## Check yourself

??? question "1. Which of these lists are min-heaps: [1, 3, 2, 6, 4, 5] and [1, 4, 2, 3, 5]?"

    Check every position $i \ge 1$ against its parent $\lfloor(i-1)/2\rfloor$. In [1, 3, 2, 6, 4, 5]: 3 and 2 have
    parent 1; 6 and 4 have parent 3; 5 has parent 2. All parents are smaller: a heap. In [1, 4, 2, 3, 5], position 3
    holds 3 and its parent at position 1 holds 4 > 3: not a heap.

??? question "2. Push 0 into the heap [1, 3, 2, 4, 8, 7, 6, 9, 5] of Figure 9.1. Then, separately, pop from the original heap."

    Push: 0 goes to position 9, whose parent is position 4 (key 8): swap. Position 4's parent is 1 (key 3): swap.
    Position 1's parent is 0 (key 1): swap. Result [0, 1, 2, 4, 3, 7, 6, 9, 5, 8].

    Pop: remove 1; the last key 5 moves to the root: [5, 3, 2, 4, 8, 7, 6, 9]. Its children are 3 and 2; swap with the
    smaller, 2. At position 2 its children are 7 and 6, both larger: stop. Result [2, 3, 5, 4, 8, 7, 6, 9].

??? question "3. Run build-heap by hand on [5, 4, 3, 2, 1]."

    $n = 5$, internal positions 1 and 0. Position 1 (key 4): children 2 and 1, swap with 1: [5, 1, 3, 2, 4].
    Position 0 (key 5): children 1 and 3, swap with 1: [1, 5, 3, 2, 4]; now at position 1, children 2 and 4, swap with
    2: [1, 2, 3, 5, 4].

??? question "4. In a min-heap of n distinct keys, where can the largest key be? Where can the second smallest be?"

    The largest key has no children (a child would have to be larger), so it is a leaf: one of positions
    $\lfloor n/2\rfloor, \dots, n-1$. The second smallest key's parent must be smaller than it, so its parent is the
    minimum: it is at position 1 or 2.

??? question "5. Show that inserting n keys one by one into an empty binary heap can cost Θ(n log n) comparisons, even though build-heap costs O(n)."

    Insert keys in decreasing order. The $i$-th key is the smallest so far, so it climbs from depth
    $\lfloor\log_2 i\rfloor$ to the root, one comparison per level: $\sum_{i=1}^{n}\lfloor\log_2 i\rfloor$ in all.
    The last half of the terms are each at least $\log_2(n/2)$, so the sum is at least $\frac n2\log_2\frac n2$,
    which is $\Omega(n\log n)$. (For $n = 100000$ the sum is 1,468,946; the program measured 14.69 per push, which is
    this sum divided by $n$.)

??? question "6. Prove the d-ary index formulas: the children of i are d i + 1, ..., d i + d, and the parent of i > 0 is ⌊(i − 1)/d⌋."

    Level $\ell$ of a complete $d$-ary tree holds $d^\ell$ nodes and starts at position
    $S_\ell = 1 + d + \dots + d^{\ell-1}$. Note $S_{\ell+1} = dS_\ell + 1$. If $i = S_\ell + j$ is the $j$-th node of
    level $\ell$, its children are the nodes $dj, \dots, dj + d - 1$ of level $\ell + 1$, at positions
    $S_{\ell+1} + dj + r = dS_\ell + 1 + dj + r = di + 1 + r$ for $r = 0, \dots, d-1$. Conversely, if $c = di + 1 + r$
    with $0 \le r < d$, then $(c - 1)/d = i + r/d$, whose floor is $i$.

??? question "7. Write the code: report the k largest keys of a stream of n keys in O(n log k) time and O(k) memory."

    Keep a **min**-heap of the $k$ largest seen so far. Its root is the smallest of them, the one to throw out when a
    bigger key arrives.

    ```python
    import heapq

    def top_k(xs, k):
        h = []
        for x in xs:
            if len(h) < k:
                heapq.heappush(h, x)
            elif x > h[0]:
                heapq.heapreplace(h, x)     # pop the root and push x in one go
        return sorted(h, reverse=True)

    print(top_k([5, 1, 9, 3, 7, 8, 2, 6], 3))   # [9, 8, 7]
    ```

    Each key costs at most one $O(\log k)$ heap operation. (Python's `heapq.nlargest` does this.)

??? question "8. Write the code: merge k sorted lists with N keys in total in O(N log k)."

    Keep a heap holding the current front of each list, as (key, list number, index). Pop the smallest, output it, and
    push the next key from the same list.

    ```python
    import heapq

    def merge_sorted(lists):
        h = [(lst[0], i, 0) for i, lst in enumerate(lists) if lst]
        heapq.heapify(h)
        out = []
        while h:
            x, i, j = heapq.heappop(h)
            out.append(x)
            if j + 1 < len(lists[i]):
                heapq.heappush(h, (lists[i][j + 1], i, j + 1))
        return out

    print(merge_sorted([[1, 4, 9], [2, 3, 10], [5, 6, 7, 8]]))   # [1, 2, ..., 10]
    ```

    The heap never holds more than $k$ entries, and each of the $N$ keys is pushed and popped once. The list number in
    the tuple also breaks ties, so keys that compare equal never force Python to compare anything else. This is the
    merge step of external merge sort ([Chapter 24](24-Algorithms-for-Big-Data-and-Many-Processors.md)); Python's
    `heapq.merge` does it lazily.

??? question "9. A binomial heap holds 100 keys. Which trees does it contain? What happens to them when one more key is inserted?"

    $100 = 1100100_2 = 64 + 32 + 4$, so it holds $B_2$, $B_5$ and $B_6$. Inserting adds a $B_0$; there is no other
    $B_0$, so nothing links: $101 = 1100101_2$, trees $B_0, B_2, B_5, B_6$.

??? question "10. Write the code: keep the running median of a stream, with O(log n) per new key."

    Keep the smaller half in a max-heap (`heapq` with negated keys) and the larger half in a min-heap, with the
    max-heap allowed one extra key. The median is the max-heap's root, or the average of the two roots.

    ```python
    import heapq

    class RunningMedian:
        def __init__(self):
            self.low, self.high = [], []      # low: max-heap (negated), high: min-heap
        def add(self, x):
            if self.low and x > -self.low[0]:
                heapq.heappush(self.high, x)
            else:
                heapq.heappush(self.low, -x)
            if len(self.low) > len(self.high) + 1:
                heapq.heappush(self.high, -heapq.heappop(self.low))
            elif len(self.high) > len(self.low):
                heapq.heappush(self.low, -heapq.heappop(self.high))
        def median(self):
            if len(self.low) > len(self.high):
                return -self.low[0]
            return (-self.low[0] + self.high[0]) / 2

    m, out = RunningMedian(), []
    for x in [5, 15, 1, 3, 8, 7]:
        m.add(x)
        out.append(m.median())
    print(out)    # [5, 10.0, 5, 4.0, 5, 6.0]
    ```

    **Invariant:** every key in `low` is at most every key in `high`, and the sizes differ by at most one. Each `add`
    does at most three heap operations.

??? question "11. In a Fibonacci heap, why is the cascading cut needed? What goes wrong without it?"

    Without it, decrease-key could cut every child but one from a node, again and again, while the node's degree had
    been earned by linking big subtrees. Lemma 9.4 (child $i$ has degree at least $i - 2$) would fail, so would the
    Fibonacci size bound, and then a node of degree $k$ could have a subtree of size about $k$. The maximum degree
    $D(n)$ could grow like $\sqrt n$ instead of $\log n$ and extract-min would no longer be $O(\log n)$ amortized. The
    marks let each node lose one child, and the cascading cut removes it from its parent on the second loss, which is
    exactly what the lemma needs.

??? question "12. Dijkstra's algorithm runs on a graph with n vertices and m edges. Compare the running times with a binary heap, a d-ary heap with d = m/n, and a Fibonacci heap, for m = n (sparse) and m = n² / 4 (dense)."

    Binary heap: $O(m\log n)$ (each of up to $m$ decrease-keys and $n$ extract-mins costs $O(\log n)$). Fibonacci:
    $O(m + n\log n)$. $d$-ary with $d = m/n$: $O(m\log_{m/n} n)$ (for $m = n$ use $d = 2$).

    - Sparse, $m = n$: binary $O(n\log n)$; Fibonacci $O(n\log n)$; $d$-ary $O(n\log n)$. All the same, and the binary
      heap wins on constants.
    - Dense, $m = n^2/4$: binary $O(n^2\log n)$; Fibonacci $O(n^2)$; $d$-ary with $d = n/4$ gives
      $O(n^2\log_{n/4} n) = O(n^2)$ as well. The $d$-ary heap matches the Fibonacci heap here with an array.

## What you learned

- A priority queue needs only the minimum, so it can keep less order than a search tree; insert and extract-min cannot
  both beat $\log n$, by the sorting lower bound.
- A binary heap is a complete tree stored in an array (children at $2i+1$, $2i+2$); sift-up and sift-down fix one
  violation along one path in $O(\log n)$.
- Build-heap sifts down from the last internal node back to the root and costs $O(n)$, because most nodes are near the
  bottom: $\sum h/2^h = 2$.
- Heapsort sorts in place in $O(n\log n)$ worst case; $d$-ary heaps make pushes cheaper and pops dearer, which suits
  Dijkstra on dense graphs.
- Decrease-key needs a position index; without one, lazy deletion works with the same $O(m\log n)$ bound.
- Leftist heaps merge along a right spine of at most $\log_2(n+1)$ nodes; binomial heaps merge like binary addition.
- Fibonacci heaps give $O(1)$ amortized insert, meld and decrease-key, proved with $\Phi = t + 2m$ and the Fibonacci
  degree bound; in practice binary, 4-ary and pairing heaps are usually faster.

**Next:** [Chapter 10](10-Union-Find-and-Range-Queries.md), union-find and range queries: structures that answer "are
these connected?" and "what is the sum of this range?" in almost constant or logarithmic time.

## Further reading

- T. H. Cormen, C. E. Leiserson, R. L. Rivest and C. Stein, *Introduction to Algorithms*, 4th ed., 2022: chapter 6
  (heapsort and priority queues); the third edition's chapter 19 covers Fibonacci heaps in full.
- R. Sedgewick and K. Wayne, *Algorithms*, 4th ed., 2011: section 2.4 (priority queues, indexed priority queues).
- D. E. Knuth, *The Art of Computer Programming*, vol. 3, 2nd ed., 1998: section 5.2.3 (heapsort and leftist trees).
- J. W. J. Williams, "Algorithm 232: Heapsort", *Communications of the ACM*, 1964.
- R. W. Floyd, "Algorithm 245: Treesort 3", *Communications of the ACM*, 1964.
- J. Vuillemin, "A data structure for manipulating priority queues", *Communications of the ACM*, 1978.
- M. L. Fredman and R. E. Tarjan, "Fibonacci heaps and their uses in improved network optimization algorithms",
  *Journal of the ACM*, 1987.
- M. L. Fredman, R. Sedgewick, D. D. Sleator and R. E. Tarjan, "The pairing heap: a new form of self-adjusting heap",
  *Algorithmica*, 1986.
- D. B. Johnson, "Priority queues with update and finding minimum spanning trees", *Information Processing Letters*,
  1975.
- M. L. Fredman, "On the efficiency of pairing heaps and related data structures", *Journal of the ACM*, 1999; S.
  Pettie, "Towards a final analysis of pairing heaps", FOCS 2005.
- G. S. Brodal, R. Lagogiannis and R. E. Tarjan, "Strict Fibonacci heaps", STOC 2012.
- On this site: the reference pages [binary heap](../../data-structures/binary-heap.md),
  [heapsort](../../sorting/heapsort.md), [Dijkstra's algorithm](../../graphs/dijkstra.md),
  [Prim's algorithm](../../graphs/prim.md) and [Huffman coding](../../greedy/huffman.md), which all run on a priority
  queue; [Chapter 8](08-Trees-and-Balanced-Search-Trees.md) for search trees and [Chapter 16](16-Shortest-Paths.md)
  for the full story of shortest paths.
