# Sort and search data guide

*Put things in order, and find them again fast. Four parts: stop at the one you need.*

[In one minute](#in-one-minute) · [Do it](#do-it) · [Expert](#expert) · [Now and next](#now-and-next)

## In one minute

Finding a word in a dictionary is fast because the words are **in order**. You open near the middle, see whether your word comes before or after, and throw away half the book. Ten halvings narrow 1,000 pages down to one page. That is **binary search**.

So sorting is worth doing when you will search many times. Sorting takes some work once; each search afterwards is almost free.

There are many ways to sort. With cards in your hand you probably slide each new card into its place: that is **insertion sort**, fine for a few cards and slow for a million. The fast methods split the pile, sort the halves and merge them (**merge sort**), or pick a middle card and put smaller ones left and bigger ones right (**quicksort**).

<figure class="play" data-play="sortfirst"><span class="ai-tag">AI-created</span><figcaption><b>Try it.</b> A list of a million items: is it worth sorting before you search? Slide the number of searches. Step counts are rough.</figcaption></figure>

## Do it

**Use the language's own sort.** It is faster and better tested than anything you will write.

=== "Python"

    ```python
    people = [("Ana", 31), ("Ben", 25), ("Cy", 31)]
    sorted(people, key=lambda p: p[1])                 # by age: Ben, Ana, Cy (ties keep their order)
    sorted(people, key=lambda p: (-p[1], p[0]))        # oldest first, then by name
    people.sort(key=lambda p: p[0])                    # in place

    import bisect
    a = [2, 5, 5, 9]
    bisect.bisect_left(a, 5)                           # 1: first position of 5
    bisect.bisect_right(a, 5)                          # 3: just after the last 5
    ```

=== "Java"

    ```java
    int[] a = {5, 2, 9, 5};
    Arrays.sort(a);                                    // primitives: dual-pivot quicksort
    int i = Arrays.binarySearch(a, 9);                 // index, or -(insertion point) - 1

    people.sort(Comparator.comparingInt(Person::age)   // objects: stable TimSort
                          .thenComparing(Person::name));
    ```

=== "C++"

    ```cpp
    std::vector<int> a{5, 2, 9, 5};
    std::sort(a.begin(), a.end());                     // usually introsort, not stable
    std::stable_sort(people.begin(), people.end(),
        [](const Person& x, const Person& y) { return x.age < y.age; });
    auto it = std::lower_bound(a.begin(), a.end(), 5); // first element >= 5
    bool found = std::binary_search(a.begin(), a.end(), 9);
    ```

**Other ways to find things fast**

| You need | Use | Python / Java / C++ |
|---|---|---|
| "Is it there?" or "what goes with this key?" | a hash table: about one step per lookup | `dict`, `set` / `HashMap` / `std::unordered_map` |
| Keys in order, plus "next bigger than x" | a balanced search tree | `sortedcontainers` / `TreeMap` / `std::map` |
| The smallest item, again and again | a heap | `heapq` / `PriorityQueue` / `std::priority_queue` |
| The top 10 of a million | a heap of size 10, or partial selection | `heapq.nlargest` / — / `std::partial_sort`, `std::nth_element` |
| Text search in a big set of documents | an inverted index | SQLite FTS5, PostgreSQL full-text, Lucene |

## Expert

### Which algorithm, and what it costs

| Algorithm | Time (average / worst) | Extra space | Stable | When it wins |
|---|---|---|---|---|
| [Insertion sort](../sorting/insertion-sort.md) | $O(n^2)$ / $O(n^2)$; $O(n)$ if nearly sorted | $O(1)$ | yes | tiny or nearly sorted inputs; the inner step of hybrid sorts |
| [Merge sort](../sorting/merge-sort.md) | $O(n \log n)$ / $O(n \log n)$ | $O(n)$ | yes | stability, linked lists, data on disk |
| [Quicksort](../sorting/quicksort.md) | $O(n \log n)$ / $O(n^2)$ | $O(\log n)$ | no | fastest in memory on average |
| [Heapsort](../sorting/heapsort.md) | $O(n \log n)$ / $O(n \log n)$ | $O(1)$ | no | guaranteed time with no extra memory |
| [Counting sort](../sorting/counting-sort.md), [radix sort](../sorting/radix-sort.md) | $O(n + k)$, $O(d(n + b))$ | $O(n + k)$ | yes | small integer keys; beats the $n \log n$ limit by not comparing |
| [Binary search](../searching/binary-search.md) | $O(\log n)$ | $O(1)$ | | sorted arrays; also [searching on the answer](../searching/binary-search-answer.md) |
| [Hash table](../data-structures/hash-table.md) | $O(1)$ / $O(n)$ | $O(n)$ | | exact lookups, no order |

No sort that only compares items can beat $\Omega(n \log n)$ comparisons in the worst case: there are $n!$ orders to tell apart, and each comparison has two outcomes. The proof is in the [Algorithms book, chapter 5](../books/algorithms/05-Sorting-by-Comparison.md).

### What the libraries really use

| Library | Algorithm |
|---|---|
| Python `sorted`, `list.sort` | Timsort (Tim Peters, 2002): finds runs already in order and merges them; the merge rule changed to Powersort in Python 3.11 |
| Java `Arrays.sort` | dual-pivot quicksort for primitives; TimSort for objects (stable) |
| C++ `std::sort` / `std::stable_sort` | introsort (quicksort that falls back to heapsort, insertion sort for short ranges) / merge sort |
| Go `slices.Sort`, `sort.Sort` | pattern-defeating quicksort (pdqsort), since Go 1.19 |
| Rust `sort` / `sort_unstable` | driftsort / ipnsort, since Rust 1.81 (2024) |
| JavaScript `Array.prototype.sort` | stable since ES2019 (V8 uses TimSort) |
| NumPy `np.sort` | introsort; SIMD-vectorized sorts on CPUs with AVX-512 |
| Databases | B-trees for indexes; external merge sort when data won't fit in memory |

### Common mistakes

| Mistake | What happens |
|---|---|
| **JavaScript's default sort on numbers** | `[10, 9, 1].sort()` gives `[1, 10, 9]`: it compares as text. Pass `(a, b) => a - b`. |
| **A comparator that isn't consistent** | Returning random results, or `a - b` that overflows on large ints, breaks the sort. Java throws "Comparison method violates its general contract!". |
| **`(low + high) / 2` overflow** | Java's own `Arrays.binarySearch` had this bug for nine years until Joshua Bloch reported it in 2006: with arrays over a billion items the sum overflows. Use `low + (high - low) / 2`. |
| **Off-by-one in binary search** | Loops that never end or miss the last item. Pick one convention (half-open `[lo, hi)`) and keep it; or use `bisect` / `lower_bound`. |
| **Assuming stability** | `std::sort` and Java's primitive sort are not stable. Sort by a tuple key, or use `stable_sort`. |
| **NaN in the data** | NaN compares false with everything, so the result can be in any order. Remove or place NaNs first. |
| **Quicksort on adversarial input** | A fixed pivot gives $O(n^2)$ on sorted data, and attackers can feed such data. Library sorts guard against this; home-made ones often don't. |
| **Sorting when a hash set would do** | Sorting to check "is x in the list" is $O(n \log n)$ work for an $O(1)$ question. |

### Best practices

- Use the built-in sort and search; write your own only to learn or for a measured need.
- Sort by a key function rather than a hand-written comparison.
- Choose the structure by the questions you will ask: exact lookup (hash), order and ranges (tree or sorted array), smallest first (heap).
- For data bigger than memory, let a database or an external sort do it.
- Measure on real data before optimizing; nearly sorted real-world data changes which method wins.

### Learn it properly

- [Algorithms book, chapter 5](../books/algorithms/05-Sorting-by-Comparison.md), [chapter 6](../books/algorithms/06-Sorting-in-Linear-Time-and-Selection.md), [chapter 7](../books/algorithms/07-Searching-and-Hashing.md), [chapter 8](../books/algorithms/08-Trees-and-Balanced-Search-Trees.md)
- [Sorting](../sorting/index.md), [Searching](../searching/index.md) and [Data structures](../data-structures/index.md) pages, with code in three languages and step-by-step animations

## Now and next

*Last checked: 4 November 2026.*

- **Even library sorts have bugs.** In 2015 de Gouw and others tried to prove TimSort correct with a verification tool and found a bug that could crash Java's and Python's sorts on large inputs; both were fixed.
- **Machines are finding faster code.** DeepMind's AlphaDev (2023) found shorter routines for sorting 3 to 5 items, now in LLVM's C++ library.
- **Hardware shapes the winner:** SIMD sorts (Google's vqsort, Intel's x86-simd-sort in NumPy) and branch-free partitioning beat classic quicksort on modern CPUs.
- **Learned indexes** (Kraska and others, 2018) replace a B-tree's search with a small model that predicts where a key lies; an active research topic for databases.
