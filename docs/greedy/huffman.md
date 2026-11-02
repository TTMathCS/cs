# Huffman coding

*Give common letters short codes and rare letters long ones, so a message takes fewer bits. Huffman's greedy
rule, "join the two rarest", builds the best such code.*

| Time | Extra space | Output |
|---|---|---|
| $O(n \log n)$ for $n$ different letters | $O(n)$ | a prefix-free code with the fewest total bits |

## The idea

A fixed-length code gives every letter the same number of bits: 6 letters need 3 bits each. But if `a` makes up
45% of a text, giving it a 1-bit code saves a lot, even if rare letters then need 4 bits.

Codes of different lengths must be **prefix-free**: no code is the start of another, so a stream of bits can be
cut into letters without separators. Such a code is a **binary tree**: letters at the leaves, 0 for a left branch,
1 for a right branch, and a letter's code is its path from the top.

Huffman's rule builds the tree **from the bottom**:

1. Every letter is a one-node tree, weighted by its count.
2. Take the **two lightest** trees and join them under a new node whose weight is their sum.
3. Repeat until one tree is left.

The rarest letters end up deepest, with the longest codes.

## How it works

1. Put every letter, with its count, into a [min-heap](../data-structures/binary-heap.md).
2. While the heap has more than one tree: pop two, join them, push the result.
3. Walk the final tree to read off the codes.

The code breaks ties by the order trees were made, so all three languages print the same codes. (Different tie
rules give different codes, all equally short.)

## Code

=== "Python"

    ```python
    --8<-- "greedy/huffman.py"
    ```

=== "Java"

    ```java
    --8<-- "greedy/Huffman.java"
    ```

=== "C++"

    ```cpp
    --8<-- "greedy/huffman.cpp"
    ```

Output: the codes `a 0`, `b 101`, `c 100`, `d 111`, `e 1101`, `f 1100`; `total bits: 224` against 300 for a fixed
3-bit code (25% less); and `face -> 110001001101`. Reading that back: `1100` can only be f, `0` is a, `100` is c,
`1101` is e.

## When to use it

- **Inside real compressors:** DEFLATE (zip, gzip, PNG) and JPEG use Huffman codes for their last step.
- **Any time symbols have very different frequencies** and you can store or agree on the code table.
- **As the textbook example of a greedy algorithm** with a clean exchange proof.

## Common mistakes

- **Joining the two most frequent** instead of the two least frequent.
- **Only one distinct letter:** the tree is a single leaf with an empty path; give it the code `0` (as the code does).
- **Forgetting to send the code table:** the decoder needs the tree, or the counts to rebuild it. Real formats
  send a compact "canonical" form.
- **Expecting compression of random data:** if all letters are equally common, Huffman can do little better than a
  fixed-length code, and nothing at all when the number of letters is a power of 2.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: a 45, b 13, c 12, d 16, e 9, f 5"

    | Step | Two lightest | New node | Trees left |
    |---|---|---|---|
    | 1 | f 5, e 9 | 14 | a 45, b 13, c 12, d 16, (14) |
    | 2 | c 12, b 13 | 25 | a 45, d 16, (14), (25) |
    | 3 | (14), d 16 | 30 | a 45, (25), (30) |
    | 4 | (25), (30) | 55 | a 45, (55) |
    | 5 | a 45, (55) | 100 | one tree |

    Code lengths: a 1, b 3, c 3, d 3, e 4, f 4. Total bits:
    $45 \cdot 1 + (13 + 12 + 16) \cdot 3 + (9 + 5) \cdot 4 = 45 + 123 + 56 = 224$.

??? abstract "The math: optimality and the entropy bound"

    For counts $f_x$ and code lengths $\ell_x$, the cost is $B = \sum_x f_x \ell_x$, where $\ell_x$ is the depth of
    $x$ in the tree.

    **Lemma 1 (exchange).** Some optimal tree has the two rarest letters $x, y$ as **siblings at the deepest
    level**. Take an optimal tree and two sibling leaves $p, q$ at the deepest level. Swapping $x$ with $p$
    changes the cost by $(f_p - f_x)(\ell_x - \ell_p) \le 0$, since $f_x \le f_p$ and $\ell_x \le \ell_p$; so the
    cost does not rise. The same for $y$ and $q$.

    **Lemma 2 (merge).** Replace $x$ and $y$ by one letter $z$ with $f_z = f_x + f_y$. A tree $T'$ for the smaller
    alphabet becomes a tree $T$ for the original by hanging $x$ and $y$ under $z$, and
    $B(T) = B(T') + f_x + f_y$. So $T$ is optimal exactly when $T'$ is.

    Huffman does exactly this merge and then solves the smaller problem the same way, so by induction its tree is
    optimal.

    **Kraft's inequality.** Lengths $\ell_x$ belong to some prefix-free binary code exactly when
    $\sum_x 2^{-\ell_x} \le 1$.

    **Entropy bound (Shannon).** With $p_x = f_x / N$, the average code length $L$ of a Huffman code satisfies

    $$H \le L < H + 1, \qquad H = -\sum_x p_x \log_2 p_x.$$

    For the example, $H \approx 2.22$ bits and $L = 2.24$ bits per letter: very close. Arithmetic coding can get
    even closer to $H$ by not rounding each letter to a whole number of bits.

??? tip "Watch it step by step"

    Orange: the two lightest trees about to be joined. Red: the new node. The line below lists what is waiting in
    the heap.

    <div class="cs-anim" data-anim="huffman"></div>

??? info "Variations and related ideas"

    - **Canonical Huffman codes:** keep only the code lengths, then assign codes in order; the table becomes tiny.
      DEFLATE does this.
    - **Two-queue method:** if the counts are already sorted, two plain queues replace the heap and the build is
      $O(n)$.
    - **Adaptive Huffman** (Faller–Gallager–Knuth, Vitter): the tree changes as the text is read; no table needed.
    - **Length-limited codes:** the package-merge algorithm finds the best code with no code longer than $L$ bits.
    - **Shannon–Fano coding**, the older top-down method, is not always optimal; Huffman found the bottom-up rule
      as a student in 1951.

## See also

- [Binary heap](../data-structures/binary-heap.md)
- [Greedy algorithms](index.md)
- [Trie](../data-structures/trie.md): another tree read by paths

## References

- D. A. Huffman, "A method for the construction of minimum-redundancy codes", *Proceedings of the IRE* 40(9), 1952.
- C. E. Shannon, "A mathematical theory of communication", *Bell System Technical Journal* 27, 1948.
- T. H. Cormen et al., *Introduction to Algorithms*, 4th ed., Section 15.3 (Huffman codes).
