# Sorting

Sorting puts values in order. It is the most studied problem in computer science because so much else gets easier
once data is sorted: [binary search](../searching/binary-search.md), finding duplicates, merging lists, finding the
median, and many greedy algorithms all start with "first, sort".

## The eight sorts on this site

| Sort | Worst time | Average time | Best time | Extra space | Stable | Idea in one line |
|---|---|---|---|---|---|---|
| [Bubble sort](bubble-sort.md) | $O(n^2)$ | $O(n^2)$ | $O(n)$ | $O(1)$ | yes | swap neighbours that are out of order, pass after pass |
| [Selection sort](selection-sort.md) | $O(n^2)$ | $O(n^2)$ | $O(n^2)$ | $O(1)$ | no | find the smallest remaining value and put it next |
| [Insertion sort](insertion-sort.md) | $O(n^2)$ | $O(n^2)$ | $O(n)$ | $O(1)$ | yes | insert each value into the sorted part on its left |
| [Merge sort](merge-sort.md) | $O(n \log n)$ | $O(n \log n)$ | $O(n \log n)$ | $O(n)$ | yes | sort both halves, then merge them |
| [Quicksort](quicksort.md) | $O(n^2)$ | $O(n \log n)$ | $O(n \log n)$ | $O(\log n)$ | no | split around a pivot, then sort each side |
| [Heapsort](heapsort.md) | $O(n \log n)$ | $O(n \log n)$ | $O(n \log n)$ | $O(1)$ | no | build a max-heap, then take the top $n$ times |
| [Counting sort](counting-sort.md) | $O(n + k)$ | $O(n + k)$ | $O(n + k)$ | $O(n + k)$ | yes | count each value (whole numbers $0..k$) |
| [Radix sort](radix-sort.md) | $O(d(n + b))$ | $O(d(n + b))$ | $O(d(n + b))$ | $O(n + b)$ | yes | stable-sort by each digit, last digit first |

**Stable** means equal values keep their original order. It matters when you sort records by one field after
another, for example by name and then by grade.

<figure class="play" data-play="sortsound"><span class="ai-tag">AI-created</span><figcaption><b>Watch and hear a sort</b> (sound on). Each comparison lights two bars and plays a note as high as the bar. Insertion and bubble sort take about n² comparisons; merge sort and quicksort about n log n, and you can hear how much sooner they finish.</figcaption></figure>

## Which one should I use?

- **In real code:** your language's built-in sort. Python's `sorted` and Java's sort for objects use **Timsort**
  (merge sort plus insertion sort, stable). Java's sort for `int[]` uses a dual-pivot quicksort. C++'s
  `std::sort` uses **introsort** (quicksort that switches to heapsort if it goes badly, and insertion sort for tiny
  pieces); `std::stable_sort` is a merge sort.
- **Small or nearly sorted lists:** insertion sort.
- **Guaranteed $O(n \log n)$ and stable:** merge sort.
- **Fast in practice, in place:** quicksort with a random pivot.
- **Guaranteed $O(n \log n)$ with $O(1)$ extra memory:** heapsort.
- **Small whole-number keys:** counting sort or radix sort, which beat the $n \log n$ limit below.

## The $n \log n$ limit

Any sort that learns about the values only by **comparing** two of them needs about $n \log_2 n$ comparisons in
the worst case. The reason: there are $n!$ possible orders, each comparison has two outcomes, so $c$ comparisons can
tell apart at most $2^c$ orders, and we need $2^c \ge n!$. Taking logarithms,

$$
c \ \ge\ \log_2 n! \ =\ n\log_2 n - n\log_2 e + O(\log n) \ =\ \Omega(n \log n).
$$

Counting sort and radix sort escape this limit because they never compare two values; they use the values as
array positions instead.
