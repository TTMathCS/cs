# 4. Arrays, lists, stacks and queues

*Every algorithm keeps its data somewhere, and where it keeps it decides what is cheap. Reading the thousandth item of a
list can take one step or a thousand; adding an item at the front can take one step or a million; it depends on how the
items sit in memory. This chapter builds the basic containers from the bottom up: the array, which is how memory
really looks; the dynamic array, which grows, and the amortized analysis that shows why growing by doubling is cheap;
the linked list, made of nodes and references; and the stack and the queue, two disciplines for adding and removing
items that turn up everywhere from checking brackets to running every function call. Along the way we separate what a
container promises (its abstract data type) from how it keeps the promise (its implementation).*

!!! abstract "In this chapter"
    **You will learn:**

    - why an array gives $O(1)$ access by index and $O(n)$ insertion in the middle
    - how a dynamic array grows, and how the aggregate and accounting methods prove $O(1)$ amortized appends
    - why the growth factor must be a multiple, not an added constant, and what each choice costs
    - singly and doubly linked lists, with a sentinel, built from scratch
    - stacks at work: bracket matching, Dijkstra's shunting-yard and the call stack
    - queues and deques in a circular buffer, and abstract data types versus implementations
    - (advanced) the potential method, and a queue built from two stacks in $O(1)$ amortized time

    **You need:** [Chapter 2](02-Measuring-Cost.md) (Big-O, the geometric sum, the RAM model of 1.5) and
    [Chapter 3](03-Recursion-and-Induction.md) (the call stack).

    **Levels:** 4.1, 4.3 and 4.4 are beginner; 4.2, 4.5 and 4.6 are intermediate; 4.7 is advanced.

## 4.1 Arrays

How does `a[i]` find the $i$-th item in one step, whatever $i$ is? The answer is the simplest data structure there is.

An **array** is a block of memory cells, one after another, all the same size, holding the items in order. If the
block starts at address $B$ and each item takes $w$ bytes, item $i$ (counting from 0) is at

$$\text{address}(a_i)=B+w\cdot i.$$

One multiplication and one addition give the address, and the RAM model reads any address in one step (1.5). So
reading or writing `a[i]` costs $O(1)$, the same for $i=0$ and $i=10^6$. This is the reason we count from 0: item $i$ is
$i$ items past the start. (The original reason was exactly this address arithmetic, in languages such as C, where `a[i]`
is defined as "the item $i$ places after the start of `a`".)

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 255" role="img" aria-label="An array of capacity 6 holding 10, 20, 30, 40 at addresses 1000 to 1040 in steps of 8. Below, the same array after inserting 15 at position 1: arrows show 40, 30 and 20 each moving one cell to the right, and 15 sits in cell 1.">
  <g font-size="12" text-anchor="middle" fill="currentColor">
    <text x="170" y="30">a[0]</text><text x="250" y="30">a[1]</text><text x="330" y="30">a[2]</text>
    <text x="410" y="30">a[3]</text><text x="490" y="30">a[4]</text><text x="570" y="30">a[5]</text>
  </g>
  <text x="10" y="68" font-size="13" fill="currentColor">before</text>
  <g stroke="currentColor" stroke-width="1.5">
    <rect x="130" y="40" width="80" height="48" fill="#9cc9ea" fill-opacity="0.4"/>
    <rect x="210" y="40" width="80" height="48" fill="#9cc9ea" fill-opacity="0.4"/>
    <rect x="290" y="40" width="80" height="48" fill="#9cc9ea" fill-opacity="0.4"/>
    <rect x="370" y="40" width="80" height="48" fill="#9cc9ea" fill-opacity="0.4"/>
    <rect x="450" y="40" width="80" height="48" fill="none" stroke-dasharray="4 3"/>
    <rect x="530" y="40" width="80" height="48" fill="none" stroke-dasharray="4 3"/>
  </g>
  <g font-size="17" text-anchor="middle" fill="currentColor">
    <text x="170" y="70">10</text><text x="250" y="70">20</text><text x="330" y="70">30</text><text x="410" y="70">40</text>
  </g>
  <g stroke="#eea66f" stroke-width="2">
    <line x1="250" y1="90" x2="330" y2="148"/><line x1="330" y1="90" x2="410" y2="148"/><line x1="410" y1="90" x2="490" y2="148"/>
  </g>
  <g fill="#eea66f">
    <polygon points="330,148 319.3,145.8 324.5,138.5"/><polygon points="410,148 399.3,145.8 404.5,138.5"/><polygon points="490,148 479.3,145.8 484.5,138.5"/>
  </g>
  <text x="10" y="170" font-size="13" fill="currentColor">after</text>
  <text x="10" y="186" font-size="13" fill="currentColor">insert(1, 15)</text>
  <g stroke="currentColor" stroke-width="1.5">
    <rect x="130" y="150" width="80" height="48" fill="#9cc9ea" fill-opacity="0.4"/>
    <rect x="210" y="150" width="80" height="48" fill="#eea66f" fill-opacity="0.6"/>
    <rect x="290" y="150" width="80" height="48" fill="#9cc9ea" fill-opacity="0.4"/>
    <rect x="370" y="150" width="80" height="48" fill="#9cc9ea" fill-opacity="0.4"/>
    <rect x="450" y="150" width="80" height="48" fill="#9cc9ea" fill-opacity="0.4"/>
    <rect x="530" y="150" width="80" height="48" fill="none" stroke-dasharray="4 3"/>
  </g>
  <g font-size="17" text-anchor="middle" fill="currentColor">
    <text x="170" y="180">10</text><text x="250" y="180">15</text><text x="330" y="180">20</text><text x="410" y="180">30</text><text x="490" y="180">40</text>
  </g>
  <g font-size="12" text-anchor="middle" fill="currentColor">
    <text x="170" y="216">1000</text><text x="250" y="216">1008</text><text x="330" y="216">1016</text>
    <text x="410" y="216">1024</text><text x="490" y="216">1032</text><text x="570" y="216">1040</text>
  </g>
  <text x="10" y="216" font-size="12" fill="currentColor">address</text>
  <text x="370" y="244" font-size="13" text-anchor="middle" fill="currentColor">address of a[i] = 1000 + 8 · i : found in one step for any i</text>
</svg>
<figcaption>An array of 8-byte items starting at address 1000. Reading a[i] is one address calculation. Inserting 15 at
position 1 must move every later item one cell to the right, starting from the end.</figcaption>
</figure>

### What arrays are bad at

The same layout that makes indexing fast makes some other things slow.

- **Inserting in the middle.** To insert $x$ at position $i$ in an array of $n$ items, every item from $i$ to $n-1$ must
  move one cell to the right, to make room. That is $n-i$ moves: $O(n)$ in the worst case (inserting at the front), and
  $n/2$ on average if $i$ is uniformly random. The figure shows inserting 15 at position 1: three moves. (It is the same
  shifting loop as Chapter 1's sorted insertion.) Moves must go from the right end leftward, or each move would overwrite
  the next item to be moved.
- **Deleting from the middle** is the mirror image: items $i+1,\dots,n-1$ move one cell left, $O(n-i)$.
- **Growing.** An array is a fixed block. The cells after it may already belong to something else, so it cannot simply
  get longer. To add an item to a full array you must get a new, larger block and copy everything over: $O(n)$.

At the **end** of an array that has spare room, insertion and deletion are $O(1)$: nothing needs to move. That
observation, plus a clever rule for growing, is the dynamic array of 4.2.

### Arrays and caches

Arrays have one more advantage that the RAM model does not show. Their items are next to each other in memory, so a loop
over an array reads memory in order, which is exactly what caches reward (2.9). Many structures that look better on paper
than an array lose to it in practice for this reason, a point to remember when we meet linked lists.

### Python's list is an array of references

A Python `list` is an array, but its cells do not hold the items themselves. Each cell holds a **reference** (the address
of an object stored elsewhere), 8 bytes on a 64-bit machine. That is how one list can hold integers, strings and other
lists at once: every cell is the same size because every cell is just an address. Indexing is still one address
calculation plus one more step to follow the reference. The costs in this chapter apply to Python lists directly:
`a[i]`, `a[i] = x`, `a.append(x)` and `a.pop()` are $O(1)$ (append amortized, as 4.2 explains), while `a.insert(0, x)`,
`a.pop(0)` and `del a[i]` are $O(n)$.

## 4.2 Dynamic arrays and amortized analysis

*Level: intermediate.* A **dynamic array** (Python's `list`, Java's `ArrayList`, C++'s `std::vector`) looks like an array
that grows without limit. It keeps a fixed block with room for **capacity** items, of which the first $n$ (its
**length**) are in use. Appending writes into the next free cell. Only when the block is full does it **resize**: get a
new block, copy the $n$ items, and free the old one.

The question is how much bigger the new block should be. Here is the whole data structure, with a counter of the copying
work, so that we can try three rules.

```python
--8<-- "books/algorithms/ch04_dynamic_array.py"
```

Output:

```
Appending n items: element copies made by resizing
        n     double (x2)            x1.5         add 100
     1000      1023 ( 1.0)      2137 ( 2.1)      4510 ( 4.5)
    10000     16383 ( 1.6)     24284 ( 2.4)    495100 (49.5)
   100000    131071 ( 1.3)    276521 ( 2.8)  49951000 (499.5)
  (in brackets: copies per append)

insert(1, 15) into [10, 20, 30, 40] -> [10, 15, 20, 30, 40]

CPython's own list: capacity changes seen through sys.getsizeof
  length at resize -> new capacity: 1->4, 5->8, 9->16, 17->24, 25->32, 33->40, 41->52, 53->64, 65->76, 77->92, 93->108, 109->128, 129->148, 149->172, 173->200
```

With doubling or growing by half, the copies per append stay below a small constant however many items we add. With
"add 100 cells each time", the copies per append grow in proportion to $n$: half a million copies per append, on average,
at $n=100{,}000$. The rest of this section proves both facts.

### Amortized cost

One append to a doubling array can be very expensive: if the array is full with $n$ items, that append copies all $n$.
So the *worst case of a single append* is $\Theta(n)$. But such appends are rare: right after a resize there is a lot of
room, and many cheap appends follow before the next one. What we really want to know is the cost of a *sequence* of
operations.

The **amortized cost** of an operation is the total cost of a worst-case sequence of $N$ operations, divided by $N$. (The
word comes from finance, where a large cost is "amortized" by spreading it over many payments.) It is a **guarantee**
about every sequence, not an average over random inputs: no probability is involved. If appends have amortized cost 3,
then *any* $N$ appends, starting from an empty array, cost at most $3N$ in total, even though one of them may cost $N$ by
itself.

There are three standard ways to prove an amortized bound. We use two here and the third in 4.7.

### The aggregate method

Add up the total cost directly.

**Theorem.** Starting from an empty array of capacity 1 that doubles when full, any sequence of $n$ appends costs at most
$3n$ elementary steps, counting one step per item written and one per item copied. So appends cost $O(1)$ amortized.

*Proof.* Each append writes its own item once: $n$ steps. Resizes happen when the length reaches the capacity, which
takes the values $1,2,4,\dots$; a resize at capacity $2^j$ copies $2^j$ items. The last resize happens at a capacity
$2^k<n$ (a resize only happens when an item beyond the current capacity arrives). So the copies total

$$1+2+4+\dots+2^k=2^{k+1}-1<2\cdot2^k<2n.$$

(The geometric sum of Chapter 2.) In all, fewer than $n+2n=3n$ steps. $\square$

The program's doubling column shows exactly these numbers: for $n=1000$ the resizes happen at capacities $1,2,\dots,512$,
and $1+2+\dots+512=1023$ copies, about one per append.

### The accounting method

The aggregate method gives a total. The **accounting method** gives each operation a price, its **amortized cost**, and
keeps a bank account of savings. When an operation's price is more than its actual cost, the difference is saved as
**credit** stored on items in the structure; when an operation costs more than its price, it pays the difference from
credit. If the credit never goes negative, the total of the prices is at least the total actual cost, so the prices are
valid amortized costs.

**Same theorem, by accounting.** Charge 3 coins for every append. One coin pays for writing the item. The other two are
left on the item as credit.

*Claim:* whenever the array is full and must double from capacity $m$ to $2m$, there are at least $m$ coins of credit
stored, enough to pay for copying the $m$ items.

*Proof.* After the previous resize (to capacity $m$, from $m/2$), the array held $m/2$ items, and the credit on them had
just been spent. Since then, $m/2$ new items have been appended to fill the array, and each carries 2 coins: $m$ coins in
all, exactly the cost of copying $m$ items. (For the first resize, from capacity 1, the single item carries 2 coins and the
copy costs 1.) So the credit never goes negative, and 3 coins per append pays for everything. $\square$

The accounting method is a way of *finding* the amortized cost: you ask "how much must each cheap operation save so that
the expensive ones are paid for?". Here the answer is "enough to copy itself and one item from the older half".

### Why the growth factor matters

Grow by a factor $g>1$ instead of 2. Resizes happen at capacities $c,cg,cg^2,\dots$, and the last one is below $n$. Read
the sum backwards: the copies are at most

$$n+\frac ng+\frac n{g^2}+\dots<n\cdot\frac{1}{1-1/g}=n\cdot\frac{g}{g-1}.$$

For $g=2$, fewer than $2n$ copies; for $g=1.5$, fewer than $3n$. The program's columns stay within these bounds (the
measured ratios wobble because of where $n$ falls between two resizes). Any constant factor $g>1$ gives $O(1)$ amortized
appends. The choice of $g$ is a trade-off:

- a **larger** $g$ copies less often but wastes more memory: just after a resize, only about $1/g$ of the block is in use;
- a **smaller** $g$ wastes less memory but copies more.

Libraries choose differently. Java's `ArrayList` grows by about 1.5; implementations of C++'s `std::vector` commonly use
2 or 1.5. CPython's list, as the program measured through `sys.getsizeof`, grows by only about one eighth each time
(capacities 4, 8, 16, 24, 32, 40, 52, 64, 76, ...: the rule in CPython's source is roughly "new size plus one eighth,
plus a small constant, rounded to a multiple of 4"). That is still geometric growth, so appends are still $O(1)$
amortized, with a larger constant and little wasted memory.

**Adding a constant is not enough.** Grow by a fixed $k$ cells each time (the "add 100" column). Resizes happen at
$k,2k,3k,\dots$, copying $k,2k,3k,\dots$ items, so $n$ appends cost about

$$k+2k+\dots+\frac nk\cdot k=k\cdot\frac{(n/k)(n/k+1)}{2}\approx\frac{n^2}{2k}$$

copies: $\Theta(n^2)$ in total, $\Theta(n)$ per append. For $n=100{,}000$ and $k=100$, the formula gives about $5\times10^7$;
the program counted $49{,}951{,}000$. A bigger constant only divides the cost by a constant. The growth must be
*proportional* to the current size.

### Shrinking

If a dynamic array also shrinks when items are removed, the rule needs care. "Halve the capacity when it is half full"
fails: at exactly half full, one append doubles it (copying $n$ items), one removal halves it again (copying $n$ items),
and alternating appends and removals cost $\Theta(n)$ each. The standard fix is to halve when the array is only a **quarter**
full. Then after any resize the array is half full, and at least $n/4$ operations must happen before the next resize, which
pays for it. Chapter 21 proves this with the potential method.

## 4.3 Linked lists

What if we want to insert in the middle often, and never want to copy everything to grow? A different layout gives up fast
indexing to make those cheap.

A **linked list** stores each item in its own small block of memory, a **node**, anywhere in memory. Each node holds its
item and a **reference** (pointer) to the next node. The list itself just remembers the first node, the **head**. The
last node's reference is a special "nothing" value: `None` in Python, `null` in Java, `nullptr` in C++.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 260" role="img" aria-label="Top: a singly linked list. A head reference points to a node holding 1, whose next reference points to a node holding 2, then 3, whose next is None. Bottom: a circular doubly linked list with a sentinel node nil. Nil, then nodes 1, 2, 3, each with prev and next references; the last node's next wraps back to the sentinel, and the sentinel's prev points to the last node.">
  <text x="20" y="53" font-size="13" fill="currentColor">head</text>
  <line x1="58" y1="48" x2="102" y2="48" stroke="currentColor" stroke-width="1.5"/>
  <polygon points="110,48 100,43.5 100,52.5" fill="currentColor"/>
  <g stroke="currentColor" stroke-width="1.5">
    <rect x="110" y="30" width="60" height="36" fill="#9cc9ea" fill-opacity="0.45"/><rect x="170" y="30" width="30" height="36" fill="none"/>
    <rect x="250" y="30" width="60" height="36" fill="#9cc9ea" fill-opacity="0.45"/><rect x="310" y="30" width="30" height="36" fill="none"/>
    <rect x="390" y="30" width="60" height="36" fill="#9cc9ea" fill-opacity="0.45"/><rect x="450" y="30" width="30" height="36" fill="none"/>
  </g>
  <g font-size="16" text-anchor="middle" fill="currentColor"><text x="140" y="54">1</text><text x="280" y="54">2</text><text x="420" y="54">3</text></g>
  <g fill="currentColor"><circle cx="185" cy="48" r="3"/><circle cx="325" cy="48" r="3"/><circle cx="465" cy="48" r="3"/></g>
  <g stroke="currentColor" stroke-width="1.5"><line x1="185" y1="48" x2="242" y2="48"/><line x1="325" y1="48" x2="382" y2="48"/><line x1="465" y1="48" x2="512" y2="48"/></g>
  <g fill="currentColor"><polygon points="250,48 240,43.5 240,52.5"/><polygon points="390,48 380,43.5 380,52.5"/><polygon points="520,48 510,43.5 510,52.5"/></g>
  <text x="526" y="53" font-size="13" fill="currentColor">None</text>
  <text x="140" y="84" font-size="11" text-anchor="middle" fill="currentColor">value</text>
  <text x="185" y="84" font-size="11" text-anchor="middle" fill="currentColor">next</text>
  <g stroke="currentColor" stroke-width="1.5">
    <rect x="30" y="150" width="100" height="40" fill="none" stroke-dasharray="5 3"/>
    <rect x="180" y="150" width="100" height="40" fill="#7ccf9a" fill-opacity="0.35"/>
    <rect x="330" y="150" width="100" height="40" fill="#7ccf9a" fill-opacity="0.35"/>
    <rect x="480" y="150" width="100" height="40" fill="#7ccf9a" fill-opacity="0.35"/>
    <line x1="205" y1="150" x2="205" y2="190"/><line x1="255" y1="150" x2="255" y2="190"/>
    <line x1="355" y1="150" x2="355" y2="190"/><line x1="405" y1="150" x2="405" y2="190"/>
    <line x1="505" y1="150" x2="505" y2="190"/><line x1="555" y1="150" x2="555" y2="190"/>
  </g>
  <g font-size="15" text-anchor="middle" fill="currentColor">
    <text x="80" y="175">nil</text><text x="230" y="175">1</text><text x="380" y="175">2</text><text x="530" y="175">3</text>
  </g>
  <g stroke="currentColor" stroke-width="1.3">
    <line x1="130" y1="160" x2="172" y2="160"/><line x1="268" y1="160" x2="322" y2="160"/><line x1="418" y1="160" x2="472" y2="160"/>
    <line x1="192" y1="180" x2="138" y2="180"/><line x1="342" y1="180" x2="288" y2="180"/><line x1="492" y1="180" x2="438" y2="180"/>
  </g>
  <g fill="currentColor">
    <polygon points="180,160 171,156 171,164"/><polygon points="330,160 321,156 321,164"/><polygon points="480,160 471,156 471,164"/>
    <polygon points="130,180 139,176 139,184"/><polygon points="280,180 289,176 289,184"/><polygon points="430,180 439,176 439,184"/>
  </g>
  <path d="M 568 150 Q 330 95 80 150" fill="none" stroke="#eea66f" stroke-width="2"/>
  <polygon points="80.0,150.0 88.8,143.5 90.7,152.2" fill="#eea66f"/>
  <path d="M 80 190 Q 330 245 568 190" fill="none" stroke="#eea66f" stroke-width="2"/>
  <polygon points="568.0,190.0 559.3,196.6 557.2,187.9" fill="#eea66f"/>
  <text x="330" y="112" font-size="12" text-anchor="middle" fill="currentColor">last node's next is the sentinel</text>
  <text x="330" y="236" font-size="12" text-anchor="middle" fill="currentColor">sentinel's prev is the last node</text>
  <text x="80" y="140" font-size="11" text-anchor="middle" fill="currentColor">sentinel</text>
</svg>
<figcaption>Top: a singly linked list; each node holds a value and a reference to the next node. Bottom: a circular doubly
linked list with a sentinel (dashed); every node has prev and next references, and the sentinel joins the two ends, so
the first and last nodes are no different from any other.</figcaption>
</figure>

### Singly linked lists

Here is a complete singly linked list in Python. A node is a tiny object with two fields; `__slots__` just tells Python
that a node has exactly these fields, which saves memory.

```python
--8<-- "books/algorithms/ch04_linked_list.py"
```

Output:

```
singly: [1, 2, 3, 4]
after insert_after(find(2), 25): [1, 2, 25, 3, 4]
after remove(3): [1, 2, 25, 4]
after reverse(): [4, 25, 2, 1]
doubly: [0, 1, 3]  pop_back -> 3  now [0, 1]
3000 random operations on each list agree with Python's list
```

Look at what each operation costs.

- **`push_front`** makes a new node whose `next` is the old head, and makes it the head: $O(1)$, however long the list.
  Compare inserting at the front of an array, which moves all $n$ items.
- **`pop_front`** moves the head to the second node: $O(1)$.
- **`insert_after(node, x)`**: if you already *have* a reference to a node, inserting after it changes two references:
  $O(1)$. No items move.
- **`find(x)`** and **indexing**: to reach the $i$-th node you must follow $i$ references from the head, because the
  nodes are scattered and nothing tells you where node $i$ is. $O(i)$, so $O(n)$ in the worst case. This is the price of
  the layout.
- **`remove(x)`** must find the node *and the one before it* (to change the earlier node's `next`), $O(n)$, and then
  unlinks it in $O(1)$.

Reversing a singly linked list in place is a classic small exercise in reference juggling. Walk along the list, turning
each `next` reference around to point backwards:

| step | prev | node | list so far (reversed part) |
|---|---|---|---|
| start | None | 1 | |
| 1 | 1 | 2 | 1 |
| 2 | 2 | 25 | 2 → 1 |
| 3 | 25 | 4 | 25 → 2 → 1 |
| 4 | 4 | None | 4 → 25 → 2 → 1 |

The invariant: `prev` is the head of the already-reversed part (the nodes passed so far, now pointing backwards), and `node`
is the head of the part not yet visited. When `node` is None, `prev` is the new head. $O(n)$ time, $O(1)$ extra space.

### Doubly linked lists and sentinels

A singly linked list cannot remove a node given only that node, because it needs the node *before* it, and it cannot
reach the end quickly. A **doubly linked list** gives every node a second reference, `prev`, to the node before it. Now:

- removing a node you hold a reference to is $O(1)$: make its neighbours point at each other;
- adding or removing at *either* end is $O(1)$, if the list also remembers its last node.

Written naively, every doubly linked list operation has special cases: is the list empty? is this the first node (no
`prev`)? the last (no `next`)? Each case is a chance for a bug. A **sentinel** removes them all. It is one extra, dummy node,
`nil`, that holds no item and is always present. The list is made **circular** through it: `nil.next` is the first node,
`nil.prev` is the last, the first node's `prev` is `nil`, and the last node's `next` is `nil`. An empty list is just `nil`
pointing to itself both ways. Now every real node has a real neighbour on both sides, so `insert_after` and `unlink` are
each four lines with no `if` at all, and `push_front`, `push_back`, `pop_front` and `pop_back` are one line each on top of
them. Sentinels cost one node of memory and save a great deal of care; CLRS uses them throughout.

### When to use which

Linked lists win when you hold references to nodes and insert or delete next to them often: the list of recently used
items in a cache (keep a dictionary from key to node, move a node to the front in $O(1)$ on each use), the free lists inside
memory allocators, the adjacency lists of graphs in some implementations, and the chains of a hash table (Chapter 7).

For a plain sequence, a dynamic array is usually better, even for some operations where a linked list has a better $O$.
Each node is a separate object: in Python, a node with two fields takes several times the memory of one reference in a
list, and walking the nodes jumps around memory instead of reading it in order, which loses the cache advantage of 2.9. A
loop over a Python list of a million items is much faster than a walk over a linked list of a million nodes. Choose a
linked list for its $O(1)$ splicing, not by default.

## 4.4 Stacks

A **stack** is a container with a discipline: items are added and removed at one end only, the **top**. The last item
**pushed** is the first one **popped**: **LIFO**, last in, first out. Think of a stack of plates. The operations are

- `push(x)`: put $x$ on top;
- `pop()`: remove and return the top item (an error if the stack is empty);
- `peek()` (or `top()`): return the top item without removing it;
- `is_empty()`.

Either a dynamic array (top at the end) or a singly linked list (top at the head) gives all four in $O(1)$ time
(amortized, for the array). In Python, a `list` with `append` and `pop` *is* a stack. The [stack and queue reference
page](../../data-structures/stack-queue.md) has versions in three languages and an animation. What makes stacks
interesting is how many problems have exactly the LIFO shape: whatever was opened most recently must be closed first.

### Bracket matching

**Problem.** Given a text, decide whether its brackets `()`, `[]`, `{}` are **balanced**: every opener has a matching
closer of the same kind, and pairs nest properly. `{[()()]}` is balanced; `([)]` is not (the `)` closes a `[`), and
`((a + b) * c` is not (one `(` is never closed).

**Algorithm.** Read left to right. Push each opener. At each closer, the stack's top must be the matching opener: pop it,
or fail if it is the wrong kind or the stack is empty. At the end, the stack must be empty.

```python
def balanced(text):
    stack = []
    for ch in text:
        if ch in "([{":
            stack.append(ch)
        elif ch in PAIRS:            # PAIRS = {")": "(", "]": "[", "}": "{"}
            if not stack or stack.pop() != PAIRS[ch]:
                return False
    return not stack
```

Trace `([)]`: push `(`, push `[`; then `)` arrives, the top is `[`, wrong kind: not balanced.

*Why it is correct.* The invariant is: after reading a prefix of the text, the stack holds exactly the openers in that
prefix that have not yet been closed, in the order they were opened, the most recent on top. In a properly nested text,
a closer must match the *most recently opened* unclosed bracket, which is exactly the top. The full proof is an induction
on the length of the prefix, in the style of Chapter 3. The algorithm reads each character once and does $O(1)$ work per
character: $\Theta(n)$ time, and $O(n)$ space in the worst case (a text of $n$ openers).

Every compiler, every code editor that highlights the matching bracket, and every program that reads JSON, HTML or
XML does a version of this.

### Evaluating expressions: the shunting-yard algorithm

How does a calculator know that `2 * (3 + 4) - 10 / 5 ^ 2` means $2\times7-10/25=13.6$, and not something read strictly
left to right? Expressions as people write them, with operators *between* their operands, are in **infix** notation, and
they need **precedence** rules (`^` before `*` and `/`, before `+` and `-`), **associativity** rules (`10 - 3 - 2` is
`(10 - 3) - 2`, but `2 ^ 3 ^ 2` is `2 ^ (3 ^ 2)`), and parentheses to override both.

There is a notation that needs none of this. In **postfix** notation, also called **reverse Polish notation** (RPN), each
operator comes *after* its operands: `3 + 4` is `3 4 +`, and `2 * (3 + 4)` is `2 3 4 + *`. Postfix is evaluated with one
stack and no rules at all: read left to right; push each number; at each operator, pop two numbers, apply the operator,
push the result. At the end the stack holds the answer. (The name honours the Polish logician Jan Łukasiewicz, who
introduced the prefix form in the 1920s.)

So evaluation splits into two steps: convert infix to postfix, then evaluate postfix. Edsger Dijkstra described the
conversion in 1961, and called it the **shunting-yard algorithm**, because operators wait on a side track (a stack) the
way railway cars wait in a shunting yard while others pass.

**Shunting-yard.** Read the tokens left to right.

1. A **number** goes straight to the output.
2. An **operator** $o$: while the top of the stack is an operator that must be applied before $o$ (higher precedence, or
   equal precedence and $o$ is left-associative), pop it to the output. Then push $o$.
3. A **`(`** is pushed.
4. A **`)`**: pop operators to the output until the `(`, then discard the `(`.
5. At the end, pop all remaining operators to the output.

The program traces it on our example:

```python
--8<-- "books/algorithms/ch04_stacks_queues.py"
```

Output:

```
balanced('{[()()]}') = True
balanced('([)]') = False
balanced('((a + b) * c') = False
balanced('f(a[i], {k: v})') = True

Shunting-yard on: 2 * ( 3 + 4 ) - 10 / 5 ^ 2
  token  output                     stack
  2      2
  *      2                          *
  (      2                          * (
  3      2 3                        * (
  +      2 3                        * ( +
  4      2 3 4                      * ( +
  )      2 3 4 +                    *
  -      2 3 4 + *                  -
  10     2 3 4 + * 10               -
  /      2 3 4 + * 10               - /
  5      2 3 4 + * 10 5             - /
  ^      2 3 4 + * 10 5             - / ^
  2      2 3 4 + * 10 5 2           - / ^
  end    2 3 4 + * 10 5 2 ^ / -
value: 13.6   check: 13.6
2 ^ 3 ^ 2 -> 2 3 2 ^ ^ = 512.0

RingQueue and TwoStackQueue agree with deque over 100,000 operations
two-stack queue: 196,154 stack moves, 1.96 per operation
ring buffer capacity at the end: 16,384 for 10,308 items
```

Follow the interesting rows. At `)`, the `+` waiting inside the parentheses is released. At `-`, the `*` on the stack has
higher precedence, so it is output first: `2 * (3 + 4)` is finished before the subtraction. At `/`, the `-` on the stack
has *lower* precedence, so it stays, and `/` is pushed above it: the division must happen first. At `^`, precedence is
higher than `/`, so it too is pushed. At the end the stack empties from the top: `^`, `/`, `-`. The postfix
`2 3 4 + * 10 5 2 ^ / -` then evaluates as $2\cdot7=14$, $5^2=25$, $10/25=0.4$, $14-0.4=13.6$. For `2 ^ 3 ^ 2`, the
right-associativity rule keeps the first `^` on the stack when the second arrives, giving `2 3 2 ^ ^`, that is
$2^9=512$, not $(2^3)^2=64$.

Each token is pushed and popped at most once, so the algorithm runs in $\Theta(n)$ time for $n$ tokens. Compilers use the
same idea (or its generalization, operator-precedence parsing) to turn arithmetic in source code into machine instructions,
and many machines evaluate with a stack: the Java virtual machine and CPython's own bytecode interpreter are stack machines.

### The call stack

The most important stack in computing is the one Chapter 3 drew: the **call stack**. Function calls are LIFO by nature: the
function called most recently must return first. When a function is called, the machine pushes a frame with its local
variables and the **return address**, the place in the caller to continue from. When it returns, it pops the frame and
jumps to that address. Recursion needs nothing special: a recursive call is just another push.

Seeing the call stack as a data structure explains two everyday things. A **stack overflow** is what happens when the pushes
outrun the memory set aside for the stack, usually because of runaway recursion. And a **traceback** (the list of
functions an error message prints) is simply the call stack's contents, read from bottom to top, at the moment of the error.
It also explains 3.7's technique for removing recursion: keep your own stack, and push what the computer would have pushed.

## 4.5 Queues and deques

A **queue** is the other natural discipline: items join at the **back** and leave from the **front**, so the first item in
is the first out: **FIFO**. A line at a shop, packets waiting at a network router, commands sent to a rover waiting to be
executed in the order they were sent, and the frontier of a breadth-first search (Chapter 15) are all queues. The operations
are `enqueue(x)` (add at the back) and `dequeue()` (remove from the front), plus `peek` and `is_empty`.

A **deque** ("double-ended queue", said "deck") allows adding and removing at both ends.

### The wrong way

A Python list as a queue, with `append` and `pop(0)`, is correct but slow: `pop(0)` removes the first cell of an array, so
every other item moves one cell left, $O(n)$ per dequeue. A queue of a million items then needs a million moves for each
dequeue. A linked list with head and tail references does give $O(1)$ for both operations, but we can keep the array's
compact layout and still have $O(1)$ at both ends.

### The circular buffer

The trick is to stop moving the items and move the *ends* instead. Keep an array `buf` of capacity $m$, an index `head` of
the front item, and the number of items $n$. The items occupy the cells

$$\text{head},\ \text{head}+1,\ \dots,\ \text{head}+n-1\quad(\text{all mod }m).$$

"Mod $m$" (the remainder on dividing by $m$) makes the array behave like a ring: after the last cell, $m-1$, comes cell 0
again. Then:

- `enqueue(x)` writes $x$ into cell $(\text{head}+n)\bmod m$ and adds 1 to $n$;
- `dequeue()` reads cell head, sets $\text{head}\leftarrow(\text{head}+1)\bmod m$, and subtracts 1 from $n$.

Neither moves any other item: both are $O(1)$. When the ring is full ($n=m$), copy the items in order into an array twice as
big, starting at cell 0, exactly as a dynamic array does, so enqueue is $O(1)$ amortized by the argument of 4.2.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 220" role="img" aria-label="A circular buffer of capacity 8. Cells 5, 6, 7, 0 and 1 hold the queue items a, b, c, d, e; cells 2, 3, 4 are free. An arrow marks head at cell 5, the front. Another marks the next free cell 2, computed as 5 plus 5 mod 8. A curved arrow under the array goes from cell 7 back to cell 0, showing the wrap-around.">
  <g font-size="12" text-anchor="middle" fill="currentColor">
    <text x="110" y="52">0</text><text x="170" y="52">1</text><text x="230" y="52">2</text><text x="290" y="52">3</text>
    <text x="350" y="52">4</text><text x="410" y="52">5</text><text x="470" y="52">6</text><text x="530" y="52">7</text>
  </g>
  <g stroke="currentColor" stroke-width="1.5">
    <rect x="80" y="60" width="60" height="50" fill="#9cc9ea" fill-opacity="0.45"/>
    <rect x="140" y="60" width="60" height="50" fill="#9cc9ea" fill-opacity="0.45"/>
    <rect x="200" y="60" width="60" height="50" fill="none" stroke-dasharray="4 3"/>
    <rect x="260" y="60" width="60" height="50" fill="none" stroke-dasharray="4 3"/>
    <rect x="320" y="60" width="60" height="50" fill="none" stroke-dasharray="4 3"/>
    <rect x="380" y="60" width="60" height="50" fill="#eea66f" fill-opacity="0.6"/>
    <rect x="440" y="60" width="60" height="50" fill="#9cc9ea" fill-opacity="0.45"/>
    <rect x="500" y="60" width="60" height="50" fill="#9cc9ea" fill-opacity="0.45"/>
  </g>
  <g font-size="17" text-anchor="middle" fill="currentColor">
    <text x="110" y="91">d</text><text x="170" y="91">e</text><text x="410" y="91">a</text><text x="470" y="91">b</text><text x="530" y="91">c</text>
  </g>
  <line x1="410" y1="22" x2="410" y2="36" stroke="currentColor" stroke-width="1.5"/>
  <polygon points="410,42 405,32 415,32" fill="currentColor"/>
  <text x="420" y="22" font-size="12" fill="currentColor">head = 5 (front: next to dequeue)</text>
  <line x1="230" y1="22" x2="230" y2="36" stroke="currentColor" stroke-width="1.5"/>
  <polygon points="230,42 225,32 235,32" fill="currentColor"/>
  <text x="220" y="22" font-size="12" text-anchor="end" fill="currentColor">next enqueue: (5 + 5) mod 8 = 2</text>
  <path d="M 530 115 Q 320 190 110 115" fill="none" stroke="#7ccf9a" stroke-width="2.5"/>
  <polygon points="110.0,115.0 120.9,114.1 117.9,122.6" fill="#7ccf9a"/>
  <text x="320" y="176" font-size="13" text-anchor="middle" fill="currentColor">after cell 7 comes cell 0: indices are taken mod 8</text>
  <text x="320" y="204" font-size="13" text-anchor="middle" fill="currentColor">queue order: a, b, c, d, e (n = 5)</text>
</svg>
<figcaption>A circular buffer of capacity 8 holding a queue of five items. The front is at cell 5; the queue runs to the
end of the array and continues at cell 0. Enqueue writes at (head + n) mod 8; dequeue advances head. No item ever moves.</figcaption>
</figure>

The program's `RingQueue` does exactly this, and checks it against Python's `collections.deque` over 100,000 random
operations. A deque fits the same ring: adding at the front writes into cell $(\text{head}-1)\bmod m$ and moves head back.

Circular buffers are everywhere that data streams through fixed memory: audio and video buffers, keyboard input, logging
the last few thousand events in a device (a rover's flight software keeps such logs), and network cards.

### Python's deque

In Python, use `collections.deque` for queues and deques: `append`, `appendleft`, `pop` and `popleft` are all $O(1)$. CPython
implements it not as one ring but as a doubly linked list of fixed-size blocks of items, which gives $O(1)$ at both ends
without ever copying everything. Indexing into the middle of a deque is $O(n)$, so it is not a replacement for a list.
(For queues shared between threads, the standard library has `queue.Queue`, which adds locking.)

## 4.6 Abstract data types and implementations

*Level: intermediate.* We have now met the same few operations implemented in very different ways. It is worth naming the
distinction, because the whole rest of the book relies on it.

An **abstract data type** (ADT) is a description of *what* a container does: a set of operations and the rules they
obey, with no mention of memory. The **stack** ADT is: operations push, pop, peek, is_empty, with the rules that
`pop()` after `push(x)` returns $x$ and leaves the stack as it was before the push, and `is_empty()` is true exactly
when every pushed item has been popped. The **queue** ADT has the same operations, with FIFO rules instead.

A **data structure** (or **implementation**) is a particular way of laying the data out in memory and coding the
operations so that the rules hold. One ADT can have many implementations, with different costs:

| ADT | operation | dynamic array | singly linked (head, tail) | doubly linked + sentinel | circular buffer |
|---|---|---|---|---|---|
| list (sequence) | get/set item $i$ | $O(1)$ | $O(i)$ | $O(i)$ | $O(1)$ |
| | insert/delete at front | $O(n)$ | $O(1)$ | $O(1)$ | $O(1)$ amortized |
| | insert/delete at back | $O(1)$ amortized | insert $O(1)$, delete $O(n)$ | $O(1)$ | $O(1)$ amortized |
| | insert/delete in the middle, given position | $O(n)$ | $O(1)$ after the node, given it | $O(1)$, given the node | $O(n)$ |
| stack | push, pop | $O(1)$ amortized | $O(1)$ at the head | $O(1)$ | $O(1)$ amortized |
| queue | enqueue, dequeue | dequeue $O(n)$ | $O(1)$ | $O(1)$ | $O(1)$ amortized |

Separating the two has three benefits.

1. **Correctness.** Code that uses a stack only through push and pop is correct for *every* correct stack
   implementation. You can prove the algorithm once, using only the ADT's rules, and reason about the data structure
   separately.
2. **Choice.** You can pick the implementation for the costs you need, or change it later, without touching the code that
   uses it. Chapter 16's Dijkstra algorithm uses a *priority queue* ADT; Chapter 9 gives several implementations, and the
   choice changes the running time from $O(V^2)$ to $O((V+E)\log V)$ without changing the algorithm.
3. **Communication.** "Put it in a queue" says exactly what is needed, and nothing about how.

Python's built-in types are implementations, and their documentation states the costs: `list` is a dynamic array,
`collections.deque` a block-linked deque, `dict` and `set` hash tables (Chapter 7). The [reference pages on data
structures](../../data-structures/stack-queue.md) list the same costs for Java's and C++'s libraries. When an algorithm
in this book says "use a stack" or "use a queue", any implementation from this chapter with $O(1)$ (amortized) operations
will do.

## 4.7 The potential method, and a queue from two stacks

*Level: advanced.* The accounting method stores credit on particular items. The **potential method** stores it in the data
structure as a whole, as a single number, and is the most powerful of the three ways to prove amortized bounds. It is the
method behind the analyses of splay trees (Chapter 8 and Chapter 21), Fibonacci heaps (Chapter 9) and union-find
(Chapter 10).

### The method

Let $D_0$ be the initial state of the data structure and $D_i$ its state after the $i$-th operation. Choose a function
$\Phi$, the **potential**, that maps each state to a real number, with

$$\Phi(D_0)=0\quad\text{and}\quad\Phi(D_i)\ge0\text{ for every }i.$$

Define the **amortized cost** of the $i$-th operation as its actual cost $c_i$ plus the change in potential:

$$\hat c_i=c_i+\Phi(D_i)-\Phi(D_{i-1}).$$

**Theorem.** For any sequence of $N$ operations, the total actual cost is at most the total amortized cost.

*Proof.* Add up the amortized costs. The potential terms **telescope**: each $\Phi(D_i)$ appears once with a plus sign and
once (in the next term) with a minus sign, so

$$\sum_{i=1}^N\hat c_i=\sum_{i=1}^Nc_i+\Phi(D_N)-\Phi(D_0)=\sum_{i=1}^Nc_i+\Phi(D_N)\ge\sum_{i=1}^Nc_i.$$

$\square$

So if every operation has amortized cost at most $k$, any $N$ operations cost at most $kN$. Think of $\Phi$ as stored
energy: cheap operations raise the potential a little (they pay more than they cost); an expensive operation releases
potential to pay for itself. Choosing $\Phi$ is the creative step: it should be large exactly when an expensive operation
is coming.

**Example: the doubling array.** Start from an empty array of capacity 0 that, when full, grows to capacity
$\max(1,2\cdot\text{capacity})$. Let $\Phi=2n-\text{cap}$, where $n$ is the length. Initially $\Phi=0$. Since the array
is always at least half full (after the first append), $2n\ge\text{cap}$, so $\Phi\ge0$.

- An append with room: actual cost 1, and $n$ goes up by 1, so $\Phi$ goes up by 2. Amortized cost $1+2=3$.
- An append that resizes, from $n=\text{cap}=m\ge1$: actual cost $m$ copies plus 1 write. Before, $\Phi=2m-m=m$. After,
  $n=m+1$ and $\text{cap}=2m$, so $\Phi=2(m+1)-2m=2$. Amortized cost $(m+1)+(2-m)=3$.
- The very first append, from capacity 0 to 1: actual cost 1, $\Phi$ goes from 0 to $2-1=1$: amortized 2.

Every append has amortized cost at most 3, the same bound as before, now proved without any bookkeeping of which coin sits
on which item. The potential is high just before a resize (when $n=\text{cap}$, $\Phi=n$) and low just after, which is
exactly the shape we needed.

### A queue from two stacks

Here is a classic puzzle that the potential method solves neatly. You have stacks, but you need a queue. Can you build one
with $O(1)$ amortized cost per operation?

**The construction.** Keep two stacks, `inbox` and `outbox`.

- `enqueue(x)`: push $x$ onto `inbox`.
- `dequeue()`: if `outbox` is empty, pop every item off `inbox` and push it onto `outbox`. Then pop `outbox`.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 250" role="img" aria-label="Two stacks side by side. The inbox on the left holds 4 at the bottom and 5 on top; an arrow labelled enqueue 6 points into its top. The outbox on the right holds 3 at the bottom, then 2, then 1 on top; an arrow labelled dequeue returns 1 leaves its top. A dashed arrow from inbox to outbox is labelled: when outbox is empty, pop everything from inbox and push onto outbox, which reverses the order.">
  <g stroke="currentColor" stroke-width="2" fill="none">
    <polyline points="110,90 110,200 210,200 210,90"/>
    <polyline points="410,70 410,200 510,200 510,70"/>
  </g>
  <g stroke="currentColor" stroke-width="1.3">
    <rect x="120" y="164" width="80" height="32" fill="#9cc9ea" fill-opacity="0.45"/>
    <rect x="120" y="130" width="80" height="32" fill="#9cc9ea" fill-opacity="0.45"/>
    <rect x="420" y="164" width="80" height="32" fill="#7ccf9a" fill-opacity="0.4"/>
    <rect x="420" y="130" width="80" height="32" fill="#7ccf9a" fill-opacity="0.4"/>
    <rect x="420" y="96" width="80" height="32" fill="#eea66f" fill-opacity="0.6"/>
  </g>
  <g font-size="16" text-anchor="middle" fill="currentColor">
    <text x="160" y="186">4</text><text x="160" y="152">5</text>
    <text x="460" y="186">3</text><text x="460" y="152">2</text><text x="460" y="118">1</text>
  </g>
  <text x="160" y="224" font-size="14" text-anchor="middle" fill="currentColor" font-weight="bold">inbox</text>
  <text x="160" y="242" font-size="12" text-anchor="middle" fill="currentColor">newest on top</text>
  <text x="460" y="224" font-size="14" text-anchor="middle" fill="currentColor" font-weight="bold">outbox</text>
  <text x="460" y="242" font-size="12" text-anchor="middle" fill="currentColor">oldest on top</text>
  <line x1="160" y1="44" x2="160" y2="114" stroke="currentColor" stroke-width="1.5"/>
  <polygon points="160,124 155,112 165,112" fill="currentColor"/>
  <text x="160" y="36" font-size="13" text-anchor="middle" fill="currentColor">enqueue(6): push</text>
  <line x1="460" y1="88" x2="460" y2="40" stroke="currentColor" stroke-width="1.5"/>
  <polygon points="460,30 455,42 465,42" fill="currentColor"/>
  <text x="470" y="24" font-size="13" fill="currentColor">dequeue() returns 1: pop</text>
  <line x1="222" y1="160" x2="398" y2="160" stroke="#eea66f" stroke-width="2" stroke-dasharray="6 4"/>
  <polygon points="408,160 396,155 396,165" fill="#eea66f"/>
  <text x="310" y="132" font-size="12" text-anchor="middle" fill="currentColor">only when outbox is empty:</text>
  <text x="310" y="148" font-size="12" text-anchor="middle" fill="currentColor">pop all of inbox, push onto outbox</text>
  <text x="310" y="180" font-size="12" text-anchor="middle" fill="currentColor">(this reverses their order)</text>
</svg>
<figcaption>A queue made of two stacks. Items 1, 2, 3 were moved to the outbox in one refill, which reversed them so the
oldest is on top; 4 and 5 arrived later and wait in the inbox until the outbox runs dry.</figcaption>
</figure>

*Why it is a correct queue.* Moving a whole stack onto another reverses its order, so after a refill the oldest item is on
top of `outbox`. Invariant: the queue's contents, front to back, are `outbox` from top to bottom followed by `inbox` from
bottom to top. Enqueue appends at the back (the top of `inbox`); dequeue removes the front (the top of `outbox`, which is
non-empty after a refill if the queue is non-empty). A refill happens only when `outbox` is empty, and it turns `inbox`
(bottom to top: oldest to newest) into `outbox` (top to bottom: oldest to newest), so the invariant still holds. The program checks it against `collections.deque` over 100,000 random operations.

*The cost.* Count one unit per push or pop on either stack. An enqueue costs 1. A dequeue costs 1, unless it refills: then
moving $m$ items costs $2m$ (a pop and a push each), so the dequeue costs $2m+1$. A single dequeue can therefore cost
$\Theta(n)$, if $n$ items are waiting in `inbox`.

**Theorem.** Starting from an empty queue, any sequence of $N$ enqueues and dequeues costs at most $3N$ units: $O(1)$
amortized per operation.

*Proof with the potential* $\Phi=2\cdot|\text{inbox}|$, twice the number of items in `inbox`. It starts at 0 and is never
negative.

- **Enqueue:** actual cost 1; `inbox` grows by 1, so $\Phi$ grows by 2. Amortized $1+2=3$.
- **Dequeue without refill:** actual cost 1; `inbox` unchanged. Amortized 1.
- **Dequeue with refill of $m$ items:** actual cost $2m+1$; `inbox` goes from $m$ items to 0, so $\Phi$ falls by $2m$.
  Amortized $(2m+1)-2m=1$.

Every operation has amortized cost at most 3, so by the theorem any $N$ operations cost at most $3N$. $\square$

The intuition the potential captures: each item is pushed onto `inbox` once, moved to `outbox` at most once, and popped
once, so it costs at most 4 units in its whole life; the potential prepays the move at the moment the item arrives. The
program's run measured 1.96 units per operation, comfortably under the bound of 3 (the bound is reached only if every
operation is an enqueue).

This construction is not just a puzzle. It is how a queue is built in purely functional languages, where data cannot be
changed in place and singly linked lists (which act as stacks) are the basic structure; Chris Okasaki's book *Purely
Functional Data Structures* (1998) studies it and its refinements, including versions in which even the worst case is
$O(1)$.

## Check yourself

??? question "1. An array of 4-byte integers starts at address 2000. What is the address of a[7]? Of a[0]?"

    $2000+4\cdot7=2028$, and $2000+4\cdot0=2000$. Counting from 0 makes the first item sit exactly at the start.

??? question "2. You insert n items one by one at the front of an initially empty array (with enough capacity). How many item moves in total?"

    The $k$-th insertion (for $k=1,\dots,n$) moves the $k-1$ items already there: $0+1+\dots+(n-1)=\frac{n(n-1)}{2}$ moves,
    $\Theta(n^2)$. Inserting at the back instead costs no moves at all; with a linked list or deque, front insertion is
    $O(1)$ each.

??? question "3. A doubling array starts with capacity 1. How many resizes and how many element copies happen during 1000 appends? During 1025?"

    Resizes happen when an append finds the array full, at lengths 1, 2, 4, ..., 512: ten resizes, copying
    $1+2+\dots+512=1023$ items (the program's figure). For 1025 appends, the array is full again at length 1024, so the 1025th
    append resizes once more: eleven resizes, $2047$ copies. The copies per append jump from about 1.02 to about 2.0, which is
    why the measured ratio in the program wobbles between 1 and 2.

??? question "4. Write the code: return the middle node of a singly linked list in one pass, without knowing its length."

    ```python
    def middle(head):
        slow = fast = head
        while fast is not None and fast.next is not None:
            slow = slow.next          # one step
            fast = fast.next.next     # two steps
        return slow
    ```

    When `fast` reaches the end, `slow` has gone half as far. For 1 → 2 → 3 → 4 → 5 it returns the node 3; for an even
    length, the second of the two middle nodes. $O(n)$ time, $O(1)$ space.

??? question "5. Write the code: a stack that also returns its minimum in O(1) time."

    ```python
    class MinStack:
        def __init__(self):
            self.items, self.mins = [], []
        def push(self, x):
            self.items.append(x)
            self.mins.append(x if not self.mins else min(x, self.mins[-1]))
        def pop(self):
            self.mins.pop()
            return self.items.pop()
        def minimum(self):
            return self.mins[-1]
    ```

    `mins[k]` is the minimum of `items[0..k]`. Push and pop keep the two stacks the same height, so the minimum of the current
    stack is always on top of `mins`. Every operation is $O(1)$ (amortized, as list appends are).

??? question "6. Convert 1 - 2 - 3 to postfix with the shunting-yard algorithm, and evaluate it."

    `1` out; `-` pushed; `2` out; the second `-` meets a `-` of equal precedence and is left-associative, so the first `-` is
    popped to the output, then the second pushed; `3` out; end: pop `-`. Postfix `1 2 - 3 -`, value $(1-2)-3=-4$. If `-` were
    wrongly treated as right-associative, you would get `1 2 3 - -`, which is $1-(2-3)=2$.

??? question "7. Evaluate the postfix expression 5 1 2 + 4 * + 3 − with a stack, showing the stack after each token."

    5: [5]. 1: [5, 1]. 2: [5, 1, 2]. +: [5, 3]. 4: [5, 3, 4]. *: [5, 12]. +: [17]. 3: [17, 3]. −: [14]. The answer is 14
    (in infix, $5+(1+2)\cdot4-3$).

??? question "8. A circular buffer of capacity 8 has head = 6 and n = 4. Which cells hold the queue? Where does the next enqueue write? What is head after two dequeues?"

    Cells 6, 7, 0, 1, in queue order. The next enqueue writes at $(6+4)\bmod8=2$. After two dequeues,
    head $=(6+2)\bmod8=0$, and $n=2$.

??? question "9. A dynamic array doubles when full and halves when it becomes half full. Show a sequence of operations that costs Θ(n) per operation."

    Fill the array to exactly capacity $m$, a power of 2 (cheap, amortized). Now append one item: it doubles to $2m$, copying
    $m$ items. Remove one: the length is $m$, half of $2m$, so it halves, copying $m$ items. Append: doubles again. Each pair
    of operations costs about $2m$ copies, so $N$ such operations cost $\Theta(Nm)$, which is $\Theta(n)$ per operation. Halving
    at a quarter full instead leaves the array half full after each resize, so at least $m/4$ operations separate two
    resizes, and the amortized cost is $O(1)$.

??? question "10. In the two-stack queue, give a sequence of n operations in which one dequeue costs about 2n units, and explain why this does not contradict the O(1) amortized bound."

    Enqueue $n-1$ items, then dequeue once: the dequeue moves all $n-1$ items, costing $2(n-1)+1$ units. But the $n-1$
    enqueues cost only 1 each, so the whole sequence of $n$ operations costs $3(n-1)+1<3n$. Amortized bounds limit the total
    over every sequence, not each operation; the expensive dequeue was paid for by the potential that the enqueues built up.

??? question "11. Use the accounting method to show that a dynamic array that grows by a factor 1.5 has amortized cost at most 4 per append."

    Charge 4 coins per append: 1 for the write, 3 saved on the item. Suppose a resize happens at capacity $C$ (full, so
    $C$ items to copy). The previous resize grew the array to capacity $C$ from $C/1.5=\tfrac23C$, when it held $\tfrac23C$
    items and the credit was spent. Since then $C-\tfrac23C=\tfrac13C$ items have been appended, each with 3 coins: $C$ coins,
    exactly the cost of copying $C$ items. So the credit never goes negative. In general, factor $g$ needs
    $1+\frac{g}{g-1}$ coins per append: 3 for $g=2$, 4 for $g=1.5$. (Rounding of capacities changes this only slightly.)

??? question "12. Prove that the bracket-matching algorithm is correct: it returns True exactly when the text is balanced."

    Define balanced texts recursively: the empty text, a non-bracket character, $AB$ for balanced $A$ and $B$, and $(A)$,
    $[A]$, $\{A\}$ for balanced $A$. Claim: for any text, after reading a prefix, the stack holds the unmatched openers of that
    prefix in order, and the algorithm has failed only if some closer in the prefix did not match the most recent unmatched
    opener. By induction on the prefix length: an opener is pushed (it is now the most recent unmatched one); a closer is
    compared with the top, which by the hypothesis is the most recent unmatched opener, and is popped if it matches. A text is
    balanced exactly when every closer matches the most recent unmatched opener and none remain unmatched at the end, which
    is exactly when the algorithm never fails and ends with an empty stack.

## What you learned

- An array computes the address of `a[i]` as base plus $w\cdot i$, so indexing is $O(1)$; inserting or deleting in the
  middle moves $O(n)$ items; arrays are cache-friendly.
- A dynamic array grows by a constant *factor* when full; the aggregate and accounting methods prove appends cost $O(1)$
  amortized, while growing by a constant amount costs $\Theta(n)$ per append.
- Amortized cost bounds the total over every sequence of operations, with no probability involved.
- Linked lists give $O(1)$ insertion and deletion next to a node you hold, at the price of $O(n)$ indexing and poor
  locality; a sentinel removes the special cases of a doubly linked list.
- Stacks (LIFO) check brackets, convert and evaluate expressions (Dijkstra's shunting-yard) and run every function call;
  queues (FIFO) and deques fit in a circular buffer with $O(1)$ operations.
- An abstract data type says what operations do; an implementation decides what they cost; algorithms should depend only on
  the ADT.
- The potential method charges each operation its actual cost plus the change in a potential $\Phi\ge0$; with
  $\Phi=2|\text{inbox}|$ it proves a queue from two stacks costs $O(1)$ amortized.

**Next:** [Chapter 5](05-Sorting-by-Comparison.md), sorting by comparing items: insertion sort, merge sort, quicksort and
heapsort, and the proof that no comparison sort can beat $n\log n$.

## Further reading

- T. H. Cormen, C. E. Leiserson, R. L. Rivest and C. Stein, *Introduction to Algorithms*, 4th ed., 2022. Chapter 10
  (elementary data structures, sentinels) and Chapter 16 (amortized analysis: aggregate, accounting and potential methods,
  dynamic tables).
- R. E. Tarjan, "Amortized Computational Complexity", *SIAM Journal on Algebraic and Discrete Methods*, 1985: the paper that
  made amortized analysis a standard tool.
- R. Sedgewick and K. Wayne, *Algorithms*, 4th ed., 2011. Section 1.3 (bags, queues and stacks; resizing arrays; Dijkstra's
  two-stack expression evaluation).
- D. E. Knuth, *The Art of Computer Programming, Volume 1: Fundamental Algorithms*, 3rd ed., 1997. Section 2.2 (linear lists:
  stacks, queues, deques, sequential and linked allocation).
- E. W. Dijkstra, "ALGOL 60 Translation", Mathematisch Centrum report, 1961 (the shunting-yard algorithm).
- C. Okasaki, *Purely Functional Data Structures*, 1998: queues from stacks and their worst-case refinements.
- On this site: [stack and queue reference page](../../data-structures/stack-queue.md),
  [hash tables](../../data-structures/hash-table.md), [Chapter 3](03-Recursion-and-Induction.md) (the call stack),
  [Chapter 2](02-Measuring-Cost.md) (the geometric sum).
