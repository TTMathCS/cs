# Hash table

*Turn each key into a number (its **hash**), and use that number to pick one of many buckets. To find the key
later, compute the same number and look in just that bucket.*

| Insert / look up / delete | Worst case | Extra space | Keeps order |
|---|---|---|---|
| $O(1)$ on average | $O(n)$ if many keys collide | $O(n)$ | no |

## The idea

A library with a million books could find any book instantly if each title told you its shelf. A **hash
function** does exactly that: it turns a key such as `"mars"` into a large number, and the number modulo the
number of buckets says which bucket the key lives in. Looking a key up means computing its hash again and checking
one bucket, not the whole collection.

Two different keys may land in the same bucket: a **collision**. With **separate chaining**, each bucket keeps a
short list of the keys that landed there. As long as the hash spreads keys evenly and the table grows when it
gets full (here, when there are more than 0.75 keys per bucket on average), each list stays short, so every
operation is $O(1)$ on average.

This is how Python's `dict` and `set`, Java's `HashMap` and C++'s `unordered_map` work (Python uses open
addressing, a cousin of chaining; see below).

## How it works

- **Hash:** for a string $s_0 s_1 \ldots s_{m-1}$, $h = s_0 \cdot 31^{m-1} + s_1 \cdot 31^{m-2} + \cdots + s_{m-1}$, kept to 32 bits
  (exactly Java's `String.hashCode`).
- **Put:** find bucket `h % buckets`; if the key is in its list, replace the value, else append it. If the load
  factor passes 0.75, double the buckets and re-insert every key.
- **Get:** scan the one bucket's list.

## Code

=== "Python"

    ```python
    --8<-- "data-structures/hash_table.py"
    ```

=== "Java"

    ```java
    --8<-- "data-structures/HashTable.java"
    ```

=== "C++"

    ```cpp
    --8<-- "data-structures/hash_table.cpp"
    ```

Output: each of the 9 distinct words with its count ("the" 3 times), then `buckets: 16 keys: 9 missing: 0` (the
table doubled from 8 when the 7th key arrived), then `96354`, the hash of `"abc"`: $97 \cdot 31^2 + 98 \cdot 31 + 99$.

## When to use it

- **Counting and grouping:** word frequencies, votes, anagram groups.
- **Seen-before checks:** removing duplicates, detecting cycles, the "last seen" map of a
  [sliding window](../searching/sliding-window.md).
- **Caching** (memoization) in [dynamic programming](../dp/index.md).
- **Two-sum in $O(n)$:** for each value $x$, check whether $t - x$ is already in a set.
- **Not** when you need keys in sorted order, the smallest key, or range queries: use a
  [search tree](bst.md) instead.

## Common mistakes

- **Mutable keys:** changing a key after inserting it (say, a list) changes its hash, and it is lost. Python
  forbids lists as keys for this reason.
- **Overriding `equals` without `hashCode`** in Java: equal objects then land in different buckets.
- **Relying on iteration order:** it is not sorted, and in most libraries it can change as the table grows.
  (Python's `dict` keeps insertion order since 3.7, but that is a Python promise, not a hash-table one.)
- **Adversarial input:** an attacker who knows the hash function can send many keys that collide, turning $O(1)$
  into $O(n)$. Languages now randomize string hashes (Python since 3.3) to prevent this.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: hashing a few words into 8 buckets"

    | Word | Hash ($\bmod 2^{32}$) | Bucket ($\bmod 8$) |
    |---|---|---|
    | the | 114801 | 1 |
    | quick | 107947501 | 5 |
    | brown | 94011702 | 6 |
    | fox | 101583 | 7 |
    | jumps | 101487109 | 5: collides with "quick", the list grows |
    | over | 3423444 | 4 |
    | the | 114801 | 1: already there, count becomes 2 |
    | lazy | 3314548 | 4: collides with "over" |

    "lazy" is the 7th distinct key, which pushes the load past $0.75 \times 8 = 6$, so the table doubles to 16
    buckets and every key is placed again by its hash mod 16.

??? abstract "The math: why the average is O(1)"

    **Simple uniform hashing.** Assume each key is equally likely to go to any of the $m$ buckets, independently.
    With $n$ keys, the **load factor** is $\alpha = n/m$, and the expected length of any bucket's list is
    $\alpha$. So:

    $$
    \mathbb{E}[\text{cost of an unsuccessful search}] = \Theta(1 + \alpha), \qquad
    \mathbb{E}[\text{cost of a successful search}] = \Theta\!\left(1 + \tfrac{\alpha}{2}\right).
    $$

    Keeping $\alpha \le 0.75$ by doubling (an $O(1)$ amortized cost, as for a
    [growing array](stack-queue.md)) makes every operation $O(1)$ on average.

    **The birthday paradox** says collisions come early: with $m$ buckets, the first collision is expected after
    only about $\sqrt{\pi m / 2}$ keys. With 365 buckets, that is about 24. So collisions must be handled, not
    avoided.

    **Universal hashing.** Pick the hash function at random from a family where any two different keys collide
    with probability at most $1/m$, for example $h_{a,b}(k) = ((ak + b) \bmod p) \bmod m$ for a prime $p$ and
    random $a \ne 0$, $b$. Then the expected cost is $O(1 + \alpha)$ for **every** input, even one chosen by an
    adversary who does not know $a$ and $b$.

    **Open addressing** (no lists: on a collision, try the next slot) with load $\alpha < 1$ needs about
    $\frac{1}{1-\alpha}$ probes for an unsuccessful search under uniform hashing: 4 probes at $\alpha = 0.75$.

??? tip "Watch it step by step"

    Each row is a bucket; red is the entry just written. (To keep the picture small it stays at 8 buckets; the
    code doubles to 16 when the 7th key arrives.)

    <div class="cs-anim" data-anim="hash-table"></div>

??? info "Variations and related ideas"

    - **Open addressing:** linear probing (fast on modern caches), quadratic probing, double hashing.
    - **Robin Hood hashing** and **Swiss tables** (Google's `absl::flat_hash_map`, Rust's `HashMap`) keep probe
      sequences short and use SIMD to check many slots at once.
    - **Cuckoo hashing:** two hash functions, two possible slots per key; look-ups take at most 2 probes.
    - **Bloom filters** answer "maybe present / surely absent" in a tiny bit array.
    - **Consistent hashing** spreads keys over servers so that adding a server moves few keys.
    - **Cryptographic hashes** (SHA-256) are a different tool: much slower, but built so that collisions cannot be
      found on purpose.

## See also

- [Binary search tree](bst.md): ordered keys, $O(\log n)$ when balanced
- [Trie](trie.md): keys that are strings, with prefix searches
- [Rabin-Karp](../strings/rabin-karp.md): the same polynomial hash, rolled along a text

## References

- T. H. Cormen et al., *Introduction to Algorithms*, 4th ed., Chapter 11 (hash tables).
- J. L. Carter, M. N. Wegman, "Universal classes of hash functions", *Journal of Computer and System Sciences* 18(2), 1979.
- D. E. Knuth, *The Art of Computer Programming, Vol. 3*, 2nd ed., §6.4 (hashing).
