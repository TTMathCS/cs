# Strings

**String matching** asks: where does a short pattern $P$ (length $m$) appear inside a long text $T$ (length $n$)?
It runs every time you press Ctrl+F, search a genome, or filter network traffic.

The obvious way tries every starting position and compares letter by letter: up to $O(nm)$ work, for example
when searching for `aaaab` in `aaaaaaaa...`. The three algorithms here all reach $O(n + m)$, in different ways.

| Page | Main idea | Time | Good for |
|---|---|---|---|
| [KMP](kmp.md) | a table of the pattern's own repeats tells how far to slide after a mismatch | $O(n + m)$ worst case | one pattern, streaming text (never goes back) |
| [Rabin-Karp](rabin-karp.md) | compare fingerprints (hashes) of windows, updated in $O(1)$ per step | $O(n + m)$ expected | many patterns of the same length; plagiarism checks |
| [Z-algorithm](z-algorithm.md) | for each position, how long a stretch matches the start | $O(n + m)$ worst case | matching, periods, many string puzzles |

Words used on these pages:

- A **prefix** of a string is a start of it (`ma` is a prefix of `mars`); a **suffix** is an end (`rs`).
- A **border** is a string that is both a proper prefix and a suffix: `ab` is a border of `abcab`.
- A string has **period** $p$ if every letter equals the one $p$ places later: `abcabca` has period 3.

Related: the [trie](../data-structures/trie.md) stores many words for prefix search, and
[edit distance](../dp/edit-distance.md) measures how different two strings are.
