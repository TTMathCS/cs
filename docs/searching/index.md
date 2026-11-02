# Searching

Finding something fast is mostly about **not looking** at most of the data. Each technique here throws away a
large part of the possibilities with every step, using an order that is already there (a sorted list, a yes/no
question whose answer flips only once, values that only grow).

| Page | Problem | Time | Needs |
|---|---|---|---|
| [Binary search](binary-search.md) | find a value, or the first value $\ge x$, in a sorted list | $O(\log n)$ | sorted data |
| [Binary search on the answer](binary-search-answer.md) | find the smallest $x$ for which a test passes | $O(\log R)$ tests | a test that is false, false, ..., then true, true |
| [Two pointers](two-pointers.md) | pairs, merges, in-place filtering | $O(n)$ | usually sorted data |
| [Sliding window](sliding-window.md) | the best stretch of consecutive values | $O(n)$ | a window that stays valid as it shrinks |

**Linear search**, checking every value one by one, is $O(n)$ and needs nothing; it is the right choice for a
short or unsorted list that you search only once. Sorting first ($O(n \log n)$) pays off when you will search many
times. For many lookups of exact keys, a [hash table](../data-structures/hash-table.md) gives $O(1)$ on average.
