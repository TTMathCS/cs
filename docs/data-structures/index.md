# Data structures

An algorithm is only as fast as the way its data is stored. A data structure is a way of organizing data so that
the operations you need are cheap. Choosing the right one often matters more than any clever trick.

| Structure | Good at | Key operations | Cost |
|---|---|---|---|
| [Stack and queue](stack-queue.md) | last-in-first-out and first-in-first-out order | push, pop / enqueue, dequeue | $O(1)$ |
| [Hash table](hash-table.md) | "is this key here, and what is its value?" | insert, look up, delete | $O(1)$ on average |
| [Binary heap](binary-heap.md) | always knowing the smallest (or largest) | push, pop-min | $O(\log n)$, peek $O(1)$ |
| [Binary search tree](bst.md) | sorted data that changes | insert, search, delete, in-order walk | $O(h)$: $O(\log n)$ when balanced |
| [Union-find](union-find.md) | which items are connected | union, find | almost $O(1)$ |
| [Fenwick tree](fenwick-tree.md) | prefix sums of changing data | add to one value, sum of a prefix | $O(\log n)$ |
| [Segment tree](segment-tree.md) | range questions (min, max, sum) on changing data | update, range query | $O(\log n)$ |
| [Trie](trie.md) | words and prefixes | insert, look up, count by prefix | $O(\text{word length})$ |

## Which one?

- Need to **look things up by a key**? A hash table. Need them **in order** as well? A balanced search tree
  (Java's `TreeMap`, C++'s `std::map`).
- Need **the next most urgent item** again and again? A heap (`heapq`, `PriorityQueue`, `std::priority_queue`).
- Need **sums or minimums over ranges** while values change? A Fenwick or segment tree.
- Need to know whether **two things are linked**, as links are added? Union-find.
- Need **autocomplete** or many words sharing prefixes? A trie.

The table below shows what each language's standard library already provides; this site builds them by hand so
you can see how they work.

| Structure | Python | Java | C++ |
|---|---|---|---|
| stack | `list` (`append`, `pop`) | `ArrayDeque` | `std::stack`, `std::vector` |
| queue | `collections.deque` | `ArrayDeque` | `std::queue`, `std::deque` |
| hash table | `dict`, `set` | `HashMap`, `HashSet` | `std::unordered_map`, `std::unordered_set` |
| heap | `heapq` | `PriorityQueue` | `std::priority_queue` |
| balanced search tree | none built in | `TreeMap`, `TreeSet` | `std::map`, `std::set` |
