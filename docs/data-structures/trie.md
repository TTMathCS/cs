# Trie

*A tree of letters. Each path from the root spells a prefix, and words that share a beginning share the same
path. Looking up a word, or every word that starts with "mar", costs only the length of the word.*

| Insert / look up a word of length $m$ | Words with a prefix | Space |
|---|---|---|
| $O(m)$ | $O(m + \text{output})$ | up to one node per letter stored |

The name comes from re*trie*val (Fredkin, 1960); most people say "try".

## The idea

Your phone suggests "march", "marble" and "mare" as soon as you type "mar". It keeps the dictionary as a
**trie**: the root has a branch for each first letter; under "m" there is a branch for each second letter; and so
on. A node is marked when a whole word ends there.

- **Insert:** walk down the letters, creating missing nodes; mark the last node.
- **Look up:** walk down; the word is present if the walk succeeds and ends on a marked node.
- **Prefix search:** walk down the prefix, then list everything below that node.
- **Count by prefix:** store in each node how many words pass through it.

The cost depends only on the length of the word, not on how many words are stored, and words never have to be
compared with each other.

## How it works

Each node keeps a map from letter to child, an `end` flag and a `count`. The code uses an ordered map (Python
sorts at listing time), so words come out in alphabetical order.

## Code

=== "Python"

    ```python
    --8<-- "data-structures/trie.py"
    ```

=== "Java"

    ```java
    --8<-- "data-structures/Trie.java"
    ```

=== "C++"

    ```cpp
    --8<-- "data-structures/trie.cpp"
    ```

Output: `True False False` ("mar" is only a prefix, "moonlit" is absent); `4 2 0` words start with "mar", "moon"
and "x"; then the words under "mar" and under "mo", in alphabetical order.

## When to use it

- **Autocomplete and spell checking.**
- **Prefix counting:** how many usernames start with "jo".
- **IP routing:** longest-prefix match on address bits (a binary trie).
- **Word games:** Boggle and crossword solvers prune any path that is not a prefix of a word.
- **Maximum XOR of two numbers:** a binary trie of the numbers' bits answers it in $O(n \cdot \text{bits})$.
- For plain exact look-ups a [hash table](hash-table.md) is usually simpler and uses less memory.

## Common mistakes

- **Forgetting the end mark:** then "mar" is reported as a word just because "mars" is stored.
- **Memory:** a node with a 26-slot array per letter wastes space on sparse data; a map per node (as here) or a
  compressed trie saves it.
- **Deleting** a word must also remove nodes that no other word uses, and fix the counts.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: the trie of mars, marble, march, mare, moon, moonlight, map"

    ```
    (root)
     └ m
       ├ a
       │ ├ p•                 map
       │ └ r                  count 4
       │   ├ b─l─e•           marble
       │   ├ c─h•             march
       │   ├ e•               mare
       │   └ s•               mars
       └ o─o─n•               moon       (count 2 at "moon")
                 └ l─i─g─h─t• moonlight
    ```

    `•` marks the end of a word. Looking up "moonlit" walks m, o, o, n, l, i, then finds no "t" child of "i":
    absent, after 6 steps.

??? abstract "The math: time and space"

    **Time.** Insert and look up visit one node per letter: $O(m)$ map operations, each $O(1)$ with a hash map,
    $O(\log \sigma)$ with an ordered map over an alphabet of $\sigma$ letters, or $O(1)$ with a $\sigma$-slot
    array. Listing the words under a prefix costs $O(m + T)$, where $T$ is the size of the subtree.

    **Space.** At most one node per letter of all the words together, $O\!\left(\sum_w |w|\right)$, and less when
    words share prefixes. With $\sigma$-slot arrays the space is $O\!\left(\sigma \sum_w |w|\right)$.

    **Comparison with a balanced search tree** of $n$ strings: a look-up makes $O(\log n)$ string comparisons, each
    up to $O(m)$, so $O(m \log n)$ in the worst case, against the trie's $O(m)$.

    **Expected depth of a random trie** of $n$ random binary strings is about $\log_2 n$, like a balanced tree,
    because random prefixes split the set roughly in half at each level.

??? tip "Watch it step by step"

    Orange is the path of the word being inserted, blue its new nodes, green nodes where a word ends.

    <div class="cs-anim" data-anim="trie"></div>

??? info "Variations and related ideas"

    - **Radix tree / Patricia trie:** chains of single-child nodes are merged into one edge with a string label.
      Used in routers and in the Linux kernel.
    - **Ternary search tree:** each node has a letter and three children (less, equal, greater); less memory
      than arrays of children.
    - **Aho–Corasick:** a trie of many patterns plus "failure links" (like [KMP](../strings/kmp.md)'s) finds every
      pattern in a text in one pass.
    - **Suffix tree / suffix trie:** a trie of all suffixes of a text answers "does this pattern occur?" in
      $O(m)$; it can be built in $O(n)$ (Ukkonen, 1995).

## See also

- [Hash table](hash-table.md): exact look-ups
- [KMP](../strings/kmp.md): pattern matching, which Aho–Corasick extends to a trie

## References

- E. Fredkin, "Trie memory", *Communications of the ACM* 3(9), 1960.
- D. E. Knuth, *The Art of Computer Programming, Vol. 3*, 2nd ed., §6.3 (digital searching).
- R. Sedgewick, K. Wayne, *Algorithms*, 4th ed., §5.2 (tries).
