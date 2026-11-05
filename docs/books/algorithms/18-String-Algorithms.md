# 18. String algorithms

*You type a word into the search box of a long document, and the matches light up at once. A biologist asks where a
short stretch of DNA occurs in a genome of three billion letters, and the answer comes back in a fraction of a
second. Both are the same question: where does one string occur inside another? In this chapter you will start with
the obvious method, see exactly how slow it can get, and then build, one idea at a time, the methods that read the
text only once (KMP, the Z-algorithm), the method that compares fingerprints instead of letters (Rabin-Karp), the
machine that looks for thousands of words at once (Aho-Corasick), and the indexes that answer a question about a
fixed text faster than you can read the text (suffix arrays, suffix trees and the Burrows-Wheeler transform).*

!!! abstract "In this chapter"
    **You will learn:**

    - why the naive search can take $nm$ steps, and which texts make it do so
    - the prefix function and the KMP algorithm, with a proof that it runs in linear time
    - the Z-algorithm, and Rabin-Karp's rolling hash with a proof of its collision probability
    - tries and the Aho-Corasick automaton for searching many patterns in one pass
    - suffix arrays by prefix doubling, the LCP array by Kasai's algorithm, and what they answer
    - suffix trees, suffix automata and the Burrows-Wheeler transform, and how they power compression and DNA search

    **You need:** [Chapter 2](02-Measuring-Cost.md) (Big-O), [Chapter 4](04-Lists-Stacks-and-Queues.md) (amortized
    counting), [Chapter 5](05-Sorting-by-Comparison.md) (sorting) and [Chapter 7](07-Searching-and-Hashing.md)
    (binary search and hashing). Arithmetic mod a prime, used in 18.3, is in
    [Chapter 19](19-Number-Theoretic-Algorithms.md) and at https://math.akadian.ca/books/.

    **Levels:** 18.1 and 18.2 are beginner to intermediate; 18.3 to 18.5 are intermediate; 18.6 is advanced.

## 18.1 Naive matching and its worst case

**The problem.** We are given a **text** $T$ of length $n$ and a **pattern** $P$ of length $m$, both strings over
some **alphabet** $\Sigma$ (the set of letters allowed: the 26 letters, the 256 byte values, or the four DNA bases
A, C, G, T). We want every **shift** $s$ (a whole number from $0$ to $n - m$) such that the pattern sits exactly
under the text there:

$$
T[s + j] = P[j] \quad \text{for every } j = 0, 1, \ldots, m - 1 .
$$

We write $T[i..j]$ for the piece of $T$ from position $i$ to position $j$, both included, and count positions from
0 as Python does. A **prefix** of a string is a piece at its start (`ban` is a prefix of `banana`), a **suffix** is a
piece at its end (`ana`), and a piece anywhere is a **substring**. The empty string is a prefix and a suffix of
everything; a **proper** prefix or suffix is one shorter than the whole string.

**The obvious method.** Try every shift. At each shift compare letters from left to right and stop at the first
mismatch:

```python
def naive(text, pat):
    n, m = len(text), len(pat)
    return [s for s in range(n - m + 1) if text[s:s + m] == pat]
```

(Python's `text[s:s+m] == pat` also stops at the first difference.) This is correct by definition: it checks the
condition above for every shift and nothing else.

**How slow can it get?** There are $n - m + 1$ shifts and each costs at most $m$ comparisons, so the cost is at most
$(n - m + 1)m$, which is $O(nm)$. Is that bound ever reached? Take $T = \texttt{aaa}\ldots\texttt{a}$ ($n$ letters) and
$P = \texttt{aa}\ldots\texttt{ab}$ ($m - 1$ letters `a` then one `b`). At every shift the first $m - 1$ letters
match and the last one fails, so every shift costs exactly $m$ comparisons and the total is exactly $(n - m + 1)m$.
With $m = n/2$ that is about $n^2/4$: for a text of a million letters, a quarter of a trillion comparisons. The
program at the end of 18.4 counts them: for $n = 10\,000$ and $m = 50$ the naive method makes $497\,550$ comparisons
($9951 \times 50$) while KMP, the next section, makes $19\,951$.

**Why it is usually fine.** On ordinary text the first comparison at a shift usually fails. If the letters were
random and independent over an alphabet of size $\sigma \ge 2$, the number of comparisons at one shift is at most
$1 + 1/\sigma + 1/\sigma^2 + \cdots \le \sigma/(\sigma - 1) \le 2$, so the expected total is under $2n$. That is why
simple library searches often start with something close to the naive loop. But inputs are not always random: DNA
has long repeats, files have runs of zeros, and an attacker can choose the worst case on purpose. We want a method
whose *worst* case is linear.

**What the naive method wastes.** Look at a failed shift. Suppose the first $q$ letters matched, $P[0..q-1] =
T[s..s+q-1]$, and then $P[q] \neq T[s+q]$. We now *know* the text letters $T[s..s+q-1]$: they are the pattern's own
first $q$ letters. The naive method forgets this and reads them again at the next shift. Every fast method in this
chapter is a way of not forgetting.

## 18.2 KMP: the prefix function

*Level: intermediate.*

**The question.** After $q$ letters matched and the next failed, which shifts could still be a match, and how do we
know without reading the text again?

Shift the pattern right by $d$. For the new shift to have any chance, the part of the pattern that now lies under
the already-read text, $P[0..q-d-1]$, must equal the text there, which is $P[d..q-1]$. So we need a string that is
both a **prefix** and a **suffix** of $P[0..q-1]$. Such a string is called a **border**. The smallest safe shift
uses the *longest* proper border; any smaller shift would line up a longer border, which does not exist.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 520 220" role="img" aria-label="KMP slide. Text ABABABCABAB. At shift 0 the pattern ABABCABAB matches four letters and fails at the fifth. The matched part ABAB has border AB, so the pattern slides to shift 2 and comparison continues at the same text letter.">
<text x="52" y="40" font-size="13" text-anchor="end" fill="currentColor">text</text>
<g font-size="14" font-family="monospace" text-anchor="middle" fill="currentColor">
<rect x="60" y="20" width="34" height="30" fill="none" stroke="currentColor"/><text x="77" y="40">A</text>
<rect x="94" y="20" width="34" height="30" fill="none" stroke="currentColor"/><text x="111" y="40">B</text>
<rect x="128" y="20" width="34" height="30" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/><text x="145" y="40">A</text>
<rect x="162" y="20" width="34" height="30" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/><text x="179" y="40">B</text>
<rect x="196" y="20" width="34" height="30" fill="#eea66f" fill-opacity="0.5" stroke="currentColor"/><text x="213" y="40">A</text>
<rect x="230" y="20" width="34" height="30" fill="none" stroke="currentColor"/><text x="247" y="40">B</text>
<rect x="264" y="20" width="34" height="30" fill="none" stroke="currentColor"/><text x="281" y="40">C</text>
<rect x="298" y="20" width="34" height="30" fill="none" stroke="currentColor"/><text x="315" y="40">A</text>
<rect x="332" y="20" width="34" height="30" fill="none" stroke="currentColor"/><text x="349" y="40">B</text>
<rect x="366" y="20" width="34" height="30" fill="none" stroke="currentColor"/><text x="383" y="40">A</text>
<rect x="400" y="20" width="34" height="30" fill="none" stroke="currentColor"/><text x="417" y="40">B</text>
</g>
<text x="52" y="100" font-size="13" text-anchor="end" fill="currentColor">s = 0</text>
<g font-size="14" font-family="monospace" text-anchor="middle" fill="currentColor">
<rect x="60" y="80" width="34" height="30" fill="#7ccf9a" fill-opacity="0.5" stroke="currentColor"/><text x="77" y="100">A</text>
<rect x="94" y="80" width="34" height="30" fill="#7ccf9a" fill-opacity="0.5" stroke="currentColor"/><text x="111" y="100">B</text>
<rect x="128" y="80" width="34" height="30" fill="#7ccf9a" fill-opacity="0.5" stroke="currentColor"/><text x="145" y="100">A</text>
<rect x="162" y="80" width="34" height="30" fill="#7ccf9a" fill-opacity="0.5" stroke="currentColor"/><text x="179" y="100">B</text>
<rect x="196" y="80" width="34" height="30" fill="#eea66f" fill-opacity="0.5" stroke="currentColor"/><text x="213" y="100">C</text>
<rect x="230" y="80" width="34" height="30" fill="none" stroke="currentColor" stroke-dasharray="3 3"/><text x="247" y="100">A</text>
<rect x="264" y="80" width="34" height="30" fill="none" stroke="currentColor" stroke-dasharray="3 3"/><text x="281" y="100">B</text>
<rect x="298" y="80" width="34" height="30" fill="none" stroke="currentColor" stroke-dasharray="3 3"/><text x="315" y="100">A</text>
<rect x="332" y="80" width="34" height="30" fill="none" stroke="currentColor" stroke-dasharray="3 3"/><text x="349" y="100">B</text>
</g>
<text x="445" y="100" font-size="12" fill="currentColor">C ≠ A</text>
<text x="52" y="170" font-size="13" text-anchor="end" fill="currentColor">s = 2</text>
<g font-size="14" font-family="monospace" text-anchor="middle" fill="currentColor">
<rect x="128" y="150" width="34" height="30" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/><text x="145" y="170">A</text>
<rect x="162" y="150" width="34" height="30" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/><text x="179" y="170">B</text>
<rect x="196" y="150" width="34" height="30" fill="#7ccf9a" fill-opacity="0.5" stroke="currentColor"/><text x="213" y="170">A</text>
<rect x="230" y="150" width="34" height="30" fill="none" stroke="currentColor"/><text x="247" y="170">B</text>
<rect x="264" y="150" width="34" height="30" fill="none" stroke="currentColor"/><text x="281" y="170">C</text>
<rect x="298" y="150" width="34" height="30" fill="none" stroke="currentColor"/><text x="315" y="170">A</text>
<rect x="332" y="150" width="34" height="30" fill="none" stroke="currentColor"/><text x="349" y="170">B</text>
<rect x="366" y="150" width="34" height="30" fill="none" stroke="currentColor"/><text x="383" y="170">A</text>
<rect x="400" y="150" width="34" height="30" fill="none" stroke="currentColor"/><text x="417" y="170">B</text>
</g>
<line x1="94" y1="118" x2="138" y2="144" stroke="currentColor" stroke-width="1.3"/>
<polygon points="145,148 134,146 140,139" fill="currentColor"/>
<text x="260" y="205" font-size="12" text-anchor="middle" fill="currentColor">the border AB is not read again</text>
</svg>
<figcaption>Figure 18.1. One KMP slide. Four letters matched (green), the fifth failed (orange). The matched part ABAB ends with AB, which is also how the pattern starts (blue), so the pattern slides by two and the text pointer does not move back.</figcaption>
</figure>

**The prefix function.** For a pattern $P$ of length $m$ define, for each $i$ from $0$ to $m - 1$,

$$
\pi[i] = \text{the length of the longest proper border of } P[0..i] .
$$

For `ABABCABAB` it is $[0, 0, 1, 2, 0, 1, 2, 3, 4]$: for instance $P[0..3] = \texttt{ABAB}$ has proper borders `AB`
and the empty string, so $\pi[3] = 2$; and $P[0..8]$, the whole pattern, ends with `ABAB`, which is also its start, so
$\pi[8] = 4$. The function depends only on the pattern, so it is computed once, before the text is read.

**Lemma 18.1 (borders of borders).** The borders of $P[0..i]$, from longest to shortest, are exactly the lengths
$\pi[i]$, $\pi[\pi[i] - 1]$, $\pi[\pi[\pi[i]-1]-1]$, and so on down to $0$.

*Proof.* Let $u$ be the longest proper border of $x = P[0..i]$. Any shorter border $v$ of $x$ is a prefix of $x$, hence
a prefix of $u$ (both are prefixes of $x$, and $v$ is shorter); and $v$ is a suffix of $x$, hence a suffix of $u$
(both are suffixes of $x$). So $v$ is a border of $u$. Conversely a border of $u$ is a prefix of $u$, so of $x$, and a
suffix of $u$, so of $x$. Hence the borders of $x$ shorter than $u$ are exactly the borders of $u$, and the longest of
those has length $\pi[|u| - 1]$. Repeat. $\square$

**Lemma 18.2 (how a border grows).** If $P[0..i]$ has a border of length $k + 1 \ge 1$, then $P[0..i-1]$ has a border
of length $k$ and $P[k] = P[i]$.

*Proof.* Remove the last letter from both copies of the border. $\square$

So to find $\pi[i]$, walk down the borders of $P[0..i-1]$, longest first, using Lemma 18.1, and take the first one,
of length $k$, whose next letter $P[k]$ equals $P[i]$; then $\pi[i] = k + 1$. If none works, $\pi[i] = 0$. That is
the whole algorithm:

```python
def prefix_function(p):
    pi = [0] * len(p)
    k = 0                       # k = pi[i-1], the current border
    for i in range(1, len(p)):
        while k > 0 and p[i] != p[k]:
            k = pi[k - 1]       # next shorter border
        if p[i] == p[k]:
            k += 1
        pi[i] = k
    return pi
```

**Trace** on `ABABCABAB`:

| $i$ | $P[i]$ | what happens | $\pi[i]$ |
|---|---|---|---|
| 0 | A | by definition | 0 |
| 1 | B | $k = 0$, B $\neq$ A | 0 |
| 2 | A | $k = 0$, A $=$ A, $k \to 1$ | 1 |
| 3 | B | B $= P[1]$, $k \to 2$ | 2 |
| 4 | C | C $\neq P[2] =$ A, fall to $k = \pi[1] = 0$; C $\neq$ A | 0 |
| 5 | A | A $= P[0]$, $k \to 1$ | 1 |
| 6 | B | B $= P[1]$, $k \to 2$ | 2 |
| 7 | A | A $= P[2]$, $k \to 3$ | 3 |
| 8 | B | B $= P[3]$, $k \to 4$ | 4 |

**Searching.** Searching is the same loop run on the text. The variable $k$ now means "the last $k$ letters read match
the first $k$ letters of the pattern". On a new text letter $c$, fall back along borders until $P[k] = c$ or $k = 0$;
if $P[k] = c$ increase $k$; when $k = m$ a match ends here, so report shift $i - m + 1$ and set $k = \pi[m - 1]$ to look
for overlapping matches. Trace on the text `ABABABCABABX`:

| $i$ | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| $T[i]$ | A | B | A | B | A | B | C | A | B | A | B | X |
| $k$ after | 1 | 2 | 3 | 4 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 0 |

At $i = 4$ the text has A where the pattern wants C, so $k$ falls from 4 to $\pi[3] = 2$, and then A $= P[2]$ makes it
3: that is Figure 18.1. At $i = 10$, $k$ reaches $9 = m$, so there is a match at shift $10 - 9 + 1 = 2$, and $k$ is set
to $\pi[8] = 4$ before X sends it to 0.

**Theorem 18.3 (KMP is correct).** After reading $T[0..i]$, $k$ is the length of the longest prefix of $P$ (shorter
than $m$, or equal to $m$ at a reported match) that is a suffix of $T[0..i]$. Hence KMP reports exactly the shifts
where $P$ occurs.

*Proof.* By induction on $i$. Before any letter, $k = 0$. Suppose the claim holds after $T[0..i-1]$ with value $k$. A
prefix $P[0..j]$ that is a suffix of $T[0..i]$ is, without its last letter, a prefix of $P$ that is a suffix of
$T[0..i-1]$ (Lemma 18.2 applied to text and pattern), so its length minus one is at most $k$ and, by Lemma 18.1 applied
to $P[0..k-1]$, is one of the lengths in the chain $k, \pi[k-1], \ldots, 0$. The loop tries these in decreasing order and
stops at the first whose next letter is $T[i]$, which therefore gives the longest. A match is exactly $k = m$. After a
match, resetting to $\pi[m-1]$ is the next candidate in the chain. $\square$

**Theorem 18.4 (linear time).** The prefix function takes $O(m)$ time and the search $O(n)$ time; in total at most
$2n$ letter comparisons in the search.

*Proof.* Watch $k$ during the search. Each text letter increases $k$ by at most 1, so over the whole text $k$ goes up
at most $n$ times in total. Each pass of the `while` loop decreases $k$ by at least 1 (because $\pi[k - 1] < k$), and
$k$ never goes below 0. A quantity that starts at 0, rises by at most $n$ in total and never goes negative can fall
by at most $n$ in total. So there are at most $n$ fallbacks over the whole run, plus one final comparison per
letter: at most $2n$ comparisons. The same argument on the pattern gives $O(m)$ for the prefix function. $\square$

This is amortized counting from [Chapter 4](04-Lists-Stacks-and-Queues.md): one letter may cause many fallbacks, but
the fallbacks are paid for by earlier increases. The value of $k$ is the potential. The program in 18.4 confirms it on
the worst case for the naive method: $19\,951 < 2 \times 10\,000$ comparisons.

**A useful by-product: periods.** A string $x$ of length $n$ has **period** $p$ if $x[i] = x[i + p]$ for all valid
$i$. A border of length $b$ is the same thing as a period $n - b$ (the string matches itself shifted by $n - b$). So
the smallest period of $x$ is $n - \pi[n - 1]$, found in linear time. For `abcabcab`, $\pi[7] = 5$ and the period is 3.

**History.** Donald Knuth found the algorithm while studying a theorem of Stephen Cook about two-way pushdown
automata, and James Morris found it independently while writing a text editor; Vaughan Pratt worked with Knuth on
it. Morris and Pratt wrote a technical report in 1970, and the joint paper, "Fast Pattern Matching in Strings", was
published in the *SIAM Journal on Computing* in 1977. The reference page [Knuth-Morris-Pratt](../../strings/kmp.md)
has the same algorithm in Python, Java and C++ and an animation.

<figure class="play" data-play="naivekmp"><span class="ai-tag">AI-created</span><figcaption>Try it: count the character comparisons of naive matching and of KMP on the same text and pattern.</figcaption></figure>

## 18.3 The Z-algorithm, Rabin-Karp and rolling hashes

*Level: intermediate.*

### The Z-function

**The question.** KMP asks "how much of the pattern ends here?". A second, equally useful question is "how much of
the string starts again here?". For a string $s$ of length $n$, define

$$
Z[i] = \text{the length of the longest common prefix of } s \text{ and } s[i..n-1] ,
$$

with $Z[0] = n$ by convention. For `aabxaab` the Z-array is $[7, 1, 0, 0, 3, 1, 0]$: at position 4 the string
`aab` starts again.

**Searching with it.** Glue the pattern, a separator letter that occurs in neither string, and the text: $s = P \#
T$. Then $Z[i] = m$ at a position inside $T$ exactly when the pattern starts there, since the separator stops every
common prefix at length $m$ or less. So a linear-time Z-algorithm gives a linear-time search.

**Computing it fast.** Keep the **Z-box**: the interval $[l, r)$ with the largest $r$ found so far such that
$s[l..r-1]$ equals $s[0..r-l-1]$ (a copy of a prefix). When we reach a position $i$ inside the box, the letters from $i$
to $r - 1$ are a copy of the letters from $i - l$ to $r - l - 1$, whose Z-value we already know. So $Z[i]$ is at least
$\min(r - i, Z[i - l])$. Start there and extend by direct comparison.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 560 190" role="img" aria-label="The Z-box. The string is a long bar. A prefix of length r minus l is shaded at the start; the same letters appear again in the box from l to r. Position i inside the box corresponds to position i minus l inside the prefix, whose Z-value is already known.">
<rect x="20" y="70" width="520" height="34" fill="none" stroke="currentColor" stroke-width="1.3"/>
<rect x="20" y="70" width="180" height="34" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/>
<rect x="300" y="70" width="180" height="34" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/>
<rect x="90" y="70" width="70" height="34" fill="#7ccf9a" fill-opacity="0.6" stroke="currentColor"/>
<rect x="370" y="70" width="70" height="34" fill="#7ccf9a" fill-opacity="0.6" stroke="currentColor"/>
<text x="20" y="60" font-size="13" text-anchor="middle" fill="currentColor">0</text>
<text x="200" y="60" font-size="13" text-anchor="middle" fill="currentColor">r − l</text>
<text x="300" y="60" font-size="13" text-anchor="middle" fill="currentColor">l</text>
<text x="480" y="60" font-size="13" text-anchor="middle" fill="currentColor">r</text>
<text x="90" y="125" font-size="13" text-anchor="middle" fill="currentColor">i − l</text>
<text x="370" y="125" font-size="13" text-anchor="middle" fill="currentColor">i</text>
<path d="M 125 136 Q 250 176 365 136" fill="none" stroke="currentColor" stroke-width="1.3" stroke-dasharray="5 4"/>
<polygon points="373,133 365.8,139.8 363.2,132.2" fill="currentColor"/>
<text x="250" y="148" font-size="12" text-anchor="middle" fill="currentColor">same letters</text>
<text x="280" y="24" font-size="13" text-anchor="middle" fill="currentColor">Z[i] ≥ min(r − i, Z[i − l]); compare past r only if needed</text>
</svg>
<figcaption>Figure 18.2. The Z-box [l, r) is a copy of the prefix of length r − l (blue). A position i inside it sees the same letters as position i − l (green), whose Z-value is already known, so only letters beyond r need new comparisons.</figcaption>
</figure>

```python
def z_function(s):
    n = len(s)
    z = [0] * n
    if n:
        z[0] = n
    l = r = 0
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
    return z
```

**Trace** on `aabxaab` ($n = 7$):

| $i$ | inside box? | start value | extra matches | $Z[i]$ | box $[l, r)$ after |
|---|---|---|---|---|---|
| 1 | no | 0 | 1 (a = a, then b $\neq$ a) | 1 | [1, 2) |
| 2 | no | 0 | 0 | 0 | [1, 2) |
| 3 | no | 0 | 0 | 0 | [1, 2) |
| 4 | no | 0 | 3 (`aab`, then end) | 3 | [4, 7) |
| 5 | yes | $\min(2, Z[1]) = 1$ | 0 | 1 | [4, 7) |
| 6 | yes | $\min(1, Z[2]) = 0$ | 0 | 0 | [4, 7) |

At $i = 5$ the box tells us, without comparing, that `a` matches; then $s[1]$ = a and $s[6]$ = b differ.

**Correctness.** If $i < r$, then $s[i..r-1] = s[i-l..r-l-1]$ because the box is a copy of a prefix. The common prefix
of $s$ with $s[i-l..]$ has length $Z[i - l]$; inside the box the same letters are compared, so the common prefix of $s$
with $s[i..]$ is at least $\min(r - i, Z[i - l])$. The `while` loop then extends by direct comparison, so the final
value is exact. If $i \ge r$ we start from 0 and compare directly.

**Theorem 18.5.** The Z-algorithm runs in $O(n)$ time.

*Proof.* Every successful comparison in the `while` loop, except possibly when the start value came from the box and
was less than $r - i$, moves the right end $i + Z[i]$ past $r$ and so increases $r$ by one. (If $Z[i - l] < r - i$, the
copy already shows a mismatch inside the box, and the loop fails at once.) Since $r$ only increases and never exceeds
$n$, there are at most $n$ successful comparisons in total, and at most one failed comparison per $i$. $\square$

Dan Gusfield's book (1997) made the Z-algorithm the standard teaching route into exact matching; the reference page
is [Z-algorithm](../../strings/z-algorithm.md).

### Rabin-Karp: compare fingerprints

**The idea.** Comparing two strings of length $m$ costs up to $m$ steps. Comparing two numbers costs one. So turn each
window of the text into a number, its **hash**, and compare that with the pattern's hash; only when the numbers are
equal do we compare letters. The trick is to update the hash of a window in $O(1)$ when it slides by one letter.

Read a string $x_0 x_1 \cdots x_{m-1}$ as a number in base $b$, reduced modulo a prime $p$:

$$
h(x) = \left( x_0 b^{m-1} + x_1 b^{m-2} + \cdots + x_{m-1} \right) \bmod p .
$$

When the window moves from $T[s..s+m-1]$ to $T[s+1..s+m]$, remove the first letter's term, shift everything one place,
and add the new letter:

$$
h_{s+1} = \left( (h_s - T[s] \, b^{m-1}) \, b + T[s+m] \right) \bmod p .
$$

This is a **rolling hash**. With $b^{m-1} \bmod p$ computed once, each slide costs a few multiplications.

**Worked example** (decimal digits, $b = 10$, $p = 13$). Pattern `31415`: $31415 \bmod 13 = 7$. Text
`2359023141526739921`. The first window is `23590`, and $23590 \bmod 13 = 8$. Slide to `35902`: with $10^4 \bmod 13 = 3$,

$$
\left( (8 - 2 \cdot 3) \cdot 10 + 2 \right) \bmod 13 = 22 \bmod 13 = 9 ,
$$

and indeed $35902 \bmod 13 = 9$. The fifteen window hashes are $8, 9, 3, 11, 0, 1, 7, 8, 4, 5, 10, 11, 7, 9, 11$.
Two windows hash to 7: at shift 6 the window is `31415`, a real match; at shift 12 it is `67399`, a **spurious hit**
(a collision) that the letter check rejects.

**How often do collisions happen?** If the hash were a random function, two different strings would collide with
probability $1/p$. Our hash is not random, but we can make it behave as if it were by choosing the *base* $b$ at
random.

**Theorem 18.6 (collision bound).** Let $x \neq y$ be strings of length $m$, let $p$ be a prime larger than every
letter value, and let $b$ be chosen uniformly at random from $\{0, 1, \ldots, p - 1\}$. Then

$$
\Pr[h(x) = h(y)] \le \frac{m - 1}{p} .
$$

*Proof.* $h(x) - h(y) \equiv \sum_{j} (x_j - y_j) b^{m-1-j} \pmod p$. Think of this as a polynomial in the unknown
$b$, with coefficients $x_j - y_j$. Since $x \neq y$ and every letter value is less than $p$, some coefficient is
nonzero mod $p$, so the polynomial is not the zero polynomial, and its degree is at most $m - 1$. Over the field of
integers mod a prime, a nonzero polynomial of degree $d$ has at most $d$ roots (the same fact as for real numbers, with
the same proof by dividing out a factor $b - r$ for each root $r$; see [Chapter 19](19-Number-Theoretic-Algorithms.md)).
A collision happens only if $b$ is one of those at most $m - 1$ roots, out of $p$ equally likely values. $\square$

**Expected running time.** There are $n - m + 1$ windows. A window that does not match collides with probability at
most $(m-1)/p$ and then costs $m$ extra comparisons. Every real match costs $m$ comparisons to confirm. So the expected
cost is

$$
O\!\left( n + m + z m + n \cdot \frac{m - 1}{p} \cdot m \right),
$$

where $z$ is the number of matches. With $p$ around $10^9$ and $m$ up to a few thousand the last term is a tiny fraction
of $n$, so the expected time is $O(n + m + zm)$. The worst case is still $O(nm)$, if every window collides; that
happens with negligible probability for a random base, but with certainty for a fixed, known base and an input built by
an adversary. The program in 18.4 shows what a small modulus does: with $p = 101$, a random text of 10 000 letters gave
86 spurious hits, and with $p = 10\,007$ or $10^9 + 7$ it gave none.

**Monte Carlo or Las Vegas?** If we always confirm a hash hit by comparing letters, the answers are always right and
only the time is random: a **Las Vegas** algorithm. If we skip the check and trust the hash, the time is always
$O(n + m)$ but an answer may be wrong with small probability: a **Monte Carlo** algorithm. [Chapter 21](21-Randomized-and-Amortized-Analysis.md)
studies the two kinds in general.

**Where rolling hashes shine.** Rabin-Karp is not faster than KMP for one pattern, but hashing generalizes where KMP
does not. To look for many patterns of the same length, put all their hashes in a set and test each window against
the set. To find a repeated substring of length $L$, hash all windows of length $L$ and look for equal hashes; with
binary search on $L$ this finds the longest repeated substring in $O(n \log n)$ expected time. To compare any two
substrings of a fixed text in $O(1)$, store prefix hashes $H[i] = h(T[0..i-1])$; then $h(T[i..j-1]) = H[j] - H[i]
b^{j-i} \bmod p$. Two-dimensional pattern matching and the "rsync" style of finding equal blocks in two files use the
same rolling idea.

**History.** Richard Karp and Michael Rabin published "Efficient randomized pattern-matching algorithms" in the
*IBM Journal of Research and Development* in 1987. Their version picks a random prime modulus rather than a random
base; the analysis is different (it counts how many primes can divide a fixed nonzero number) but the conclusion is
the same. See also the reference page [Rabin-Karp](../../strings/rabin-karp.md).

## 18.4 Many patterns: tries and Aho-Corasick

**The problem.** A virus scanner has a list of thousands of byte signatures; a spam filter has a list of banned
phrases; a biologist has a list of short DNA probes. Running KMP once per pattern costs $O(k n)$ for $k$ patterns.
Can we read the text once and find every occurrence of every pattern?

### Tries

A **trie** (from "retrieval"; usually said "try") stores a set of strings as a rooted tree. Each edge is labelled by
one letter, the edges leaving a node have different letters, and each node stands for the string spelled on the path
from the root to it. A node is marked if its string is in the set. Looking up a word of length $m$ follows $m$ edges,
whatever the number of stored words. The trie for $\{\texttt{he}, \texttt{she}, \texttt{his}, \texttt{hers}\}$ has ten
nodes, counting the root, one for each distinct prefix: $\varepsilon$, h, he, s, sh, she, hi, his, her, hers.
Building it costs $O(M)$ where $M$ is the total length of the patterns (times the cost of looking up a child, $O(1)$
with a table indexed by letter or a hash map). The reference page [Trie](../../data-structures/trie.md) builds one with
insert, search and prefix queries.

Now slide a trie along the text: start at the root, follow the edge for each text letter, and report when you reach a
marked node. That finds the patterns that start at the point where you began, but when an edge is missing you would
have to go back in the text and start again, which is the naive method's waste again. The fix is KMP's fix.

### Failure links

**Definition.** For a trie node $u$ standing for the string $w(u)$, its **failure link** $f(u)$ is the node for the
longest proper suffix of $w(u)$ that is also in the trie (that is, is a prefix of some pattern). The root's failure
link is the root.

This is the prefix function spread over a tree. In the example, sh has failure link h (the suffix h is a prefix of he),
she has failure link he, his and hers both have failure link s, and every other node fails to the root.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 560 310" role="img" aria-label="The Aho-Corasick automaton for he, she, his, hers. A trie with root at the top, branches h then e then r then s, h then i then s, and s then h then e. Dashed failure links go from sh to h, from she to he, and from his and hers to s. Nodes for complete patterns are shaded green.">
<g stroke="currentColor" stroke-width="1.5">
<line x1="300" y1="30" x2="200" y2="90"/>
<line x1="300" y1="30" x2="460" y2="90"/>
<line x1="200" y1="90" x2="120" y2="150"/>
<line x1="200" y1="90" x2="280" y2="150"/>
<line x1="120" y1="150" x2="120" y2="210"/>
<line x1="120" y1="210" x2="120" y2="270"/>
<line x1="280" y1="150" x2="280" y2="210"/>
<line x1="460" y1="90" x2="460" y2="150"/>
<line x1="460" y1="150" x2="460" y2="210"/>
</g>
<g stroke="#eea66f" stroke-width="1.6" stroke-dasharray="6 4" fill="none">
<line x1="444" y1="145" x2="216" y2="95"/>
<line x1="444" y1="207" x2="136" y2="153"/>
<line x1="293" y1="201" x2="449" y2="102"/>
<line x1="133" y1="261" x2="447" y2="100"/>
</g>
<g fill="#eea66f">
<polygon points="216,95 226,93 224,101"/>
<polygon points="136,153 146,151 144,159"/>
<polygon points="449,102 444,110 440,103"/>
<polygon points="447,100 442,108 438,101"/>
</g>
<g stroke="currentColor" stroke-width="1.3" font-size="14" text-anchor="middle">
<circle cx="300" cy="30" r="16" style="fill:var(--md-default-bg-color)"/>
<circle cx="200" cy="90" r="16" style="fill:var(--md-default-bg-color)"/>
<circle cx="460" cy="90" r="16" style="fill:var(--md-default-bg-color)"/>
<circle cx="120" cy="150" r="16" fill="#7ccf9a"/>
<circle cx="280" cy="150" r="16" style="fill:var(--md-default-bg-color)"/>
<circle cx="120" cy="210" r="16" style="fill:var(--md-default-bg-color)"/>
<circle cx="120" cy="270" r="16" fill="#7ccf9a"/>
<circle cx="280" cy="210" r="16" fill="#7ccf9a"/>
<circle cx="460" cy="150" r="16" style="fill:var(--md-default-bg-color)"/>
<circle cx="460" cy="210" r="16" fill="#7ccf9a"/>
</g>
<g font-size="14" text-anchor="middle" fill="currentColor">
<text x="300" y="35">ε</text>
<text x="200" y="95">h</text>
<text x="460" y="95">s</text>
<text x="120" y="155">e</text>
<text x="280" y="155">i</text>
<text x="120" y="215">r</text>
<text x="120" y="275">s</text>
<text x="280" y="215">s</text>
<text x="460" y="155">h</text>
<text x="460" y="215">e</text>
</g>
<g font-size="11" fill="currentColor">
<text x="324" y="26">0</text>
<text x="180" y="86" text-anchor="end">1</text>
<text x="484" y="86">3</text>
<text x="98" y="146" text-anchor="end">2 he</text>
<text x="300" y="146">6</text>
<text x="98" y="206" text-anchor="end">8</text>
<text x="98" y="275" text-anchor="end">9 hers</text>
<text x="302" y="224">7 his</text>
<text x="484" y="146">4</text>
<text x="484" y="214">5 she</text>
</g>
</svg>
<figcaption>Figure 18.3. The Aho-Corasick automaton for he, she, his, hers. Each node shows the letter on the edge into it and its state number; green nodes end a pattern. Dashed orange arrows are the failure links that do not go to the root (all others do). The output link of state 5 (she) points to state 2 (he), because he is a suffix of she.</figcaption>
</figure>

**The automaton.** Searching keeps a current node $u$, which stands for the longest suffix of the text read so far
that is a prefix of some pattern (compare Theorem 18.3). On a text letter $c$: while $u$ has no child for $c$ and is not
the root, set $u = f(u)$; then move to the child for $c$ if there is one, otherwise stay at the root. At every node,
report the pattern that ends there (if marked) and also every pattern that is a suffix of $w(u)$. Those are found by
following **output links** (also called dictionary links): from $u$, the nearest node on the failure chain that is
marked. In the example, state 5 (she) has output link 2 (he).

**Building the failure links.** Process nodes in order of depth, by breadth-first search
([Chapter 15](15-Graphs-and-Graph-Search.md)), so that all shorter strings are done first. For a child $v$ of $u$ along
letter $c$: walk $g = f(u), f(f(u)), \ldots$ until $g$ has a child along $c$ or $g$ is the root, and set $f(v)$ to that
child (or the root). This is Lemma 18.2 again: the longest proper suffix of $w(u)c$ that is in the trie is $w(g)c$ for
the longest suffix $w(g)$ of $w(u)$ in the trie that can be extended by $c$.

**Trace** on the text `ushers`:

| letter | u | s | h | e | r | s |
|---|---|---|---|---|---|---|
| state after | 0 | 3 (s) | 4 (sh) | 5 (she) | 8 (her) | 9 (hers) |
| reported | | | | she, he | | hers |

At `e` the automaton reaches she, reports it, and follows the output link to he. At `r`, state 5 has no child `r`, so
it fails to state 2 (he), which has one, and moves to 8 (her). No letter of the text is read twice.

**Theorem 18.7 (Aho and Corasick 1975).** Building the automaton takes $O(M)$ time (for a fixed alphabet), and
searching a text of length $n$ takes $O(n + z)$ time, where $z$ is the number of reported occurrences.

*Proof sketch.* For the search, the depth of the current node plays the role of $k$ in Theorem 18.4: each letter
raises it by at most one and each failure step lowers it by at least one, so there are at most $n$ failure steps.
Each step along an output link reports a new occurrence, so those cost $O(z)$. For construction, apply the same
argument along each pattern separately: while computing the failure links of the nodes on the path of one pattern of
length $m_j$, the depth of $f$ rises by at most one per node and falls with each step, so that path costs $O(m_j)$, and
the sum over patterns is $O(M)$. $\square$

Note that $z$ can be much larger than $n$: with patterns `a`, `aa`, `aaa`, ... every position of a text of `a`s ends
many matches. Reporting them all must cost $z$; the output links make sure we spend nothing else.

**History.** Alfred Aho and Margaret Corasick published "Efficient String Matching: An Aid to Bibliographic Search" in
*Communications of the ACM* in 1975, from work at Bell Labs on searching citations. The paper predates the KMP journal
paper and builds the same failure-function idea for a set of keywords.

Here is all of 18.1 to 18.4 in one program, every method built from scratch and checked against the naive method on
2000 random cases:

```python
--8<-- "books/algorithms/ch18_matching.py"
```

```
1. Naive matching, worst case
   n=   100 m=50: naive    2550 comparisons, KMP    151
   n=  1000 m=50: naive   47550 comparisons, KMP   1951
   n= 10000 m=50: naive  497550 comparisons, KMP  19951
2. Prefix function
   ABABCABAB [0, 0, 1, 2, 0, 1, 2, 3, 4]
   aabaaab [0, 1, 0, 1, 2, 2, 3]
   abacaba [0, 0, 1, 0, 1, 2, 3]
3. Z-function
   aabxaab [7, 1, 0, 0, 3, 1, 0]
   abacaba [7, 0, 1, 0, 3, 0, 1]
4. Same answers from four methods on ABABDABACDABABCABABABABCABAB
   naive       [10, 19]
   KMP         [10, 19]
   Z           [10, 19]
   Rabin-Karp  [10, 19]
5. Random tests against naive
   2000 random cases agree: True
6. Rabin-Karp with a tiny modulus shows collisions
   mod=       101: 11 matches, 86 false hash hits
   mod=     10007: 11 matches, 0 false hash hits
   mod=1000000007: 11 matches, 0 false hash hits
7. Aho-Corasick
   fail links: [0, 0, 0, 0, 1, 2, 0, 3, 0, 3]
   'ushers' -> [(1, 'she'), (2, 'he'), (2, 'hers')]
   'ahishers' -> [(1, 'his'), (3, 'she'), (4, 'he'), (4, 'hers')]
```

The naive count grows like $nm$ and the KMP count like $2n$. The failure links printed in part 7 are those of Figure
18.3.

## 18.5 Suffix arrays and the LCP array

**The question changes.** So far each search read the whole text. But often the text is fixed and the patterns keep
coming: a genome is searched with millions of short reads; a book is searched by many readers. Then it pays to
**preprocess the text** once into an **index**, after which each query costs time depending on the pattern, not on
$n$.

The key observation: *$P$ occurs at position $i$ of $T$ exactly when $P$ is a prefix of the suffix $T[i..n-1]$.* So
if we sort all $n$ suffixes alphabetically, the suffixes that start with $P$ form one contiguous block of the sorted
list (all strings with a given prefix are next to each other in sorted order), and binary search finds the block.

**Definition.** The **suffix array** $SA$ of $T$ is the list of starting positions of the suffixes of $T$ in sorted
order. For `banana`:

| $j$ | $SA[j]$ | suffix | $LCP[j]$ |
|---|---|---|---|
| 0 | 5 | a | 0 |
| 1 | 3 | ana | 1 |
| 2 | 1 | anana | 3 |
| 3 | 0 | banana | 0 |
| 4 | 4 | na | 0 |
| 5 | 2 | nana | 2 |

The last column, the **LCP array**, gives the length of the longest common prefix of each suffix with the one just
above it ($LCP[0] = 0$). We will build it in a moment.

**Searching.** Binary search on $SA$ for the first suffix that is not less than $P$ (comparing only the first $m$
letters), and again for the first suffix whose first $m$ letters are greater than $P$; the block between them is the
answer. Each comparison costs $O(m)$ and there are $O(\log n)$ of them, so a query costs $O(m \log n)$, plus the number
of occurrences to list them. For `ana` in `banana` the block is rows 1 and 2, positions 3 and 1. (Manber and Myers
showed how to use LCP information to cut this to $O(m + \log n)$; the details are in their paper.)

**Building it: why not just sort?** Sorting the suffixes with a comparison sort costs $O(n \log n)$ comparisons, but
one comparison of two suffixes can cost $O(n)$ letters (think of `aaaa...a`). That gives $O(n^2 \log n)$ in the worst
case. We need to reuse work between comparisons.

### Prefix doubling

**The idea** (Manber and Myers 1990, and Karp, Miller and Rosenberg 1972 before them). Sort the suffixes by their
first 1 letter, then by their first 2, then 4, then 8, and so on. The point is that the order by the first $2k$
letters can be read off from the order by the first $k$ letters, without looking at letters at all.

Give each suffix $i$ a **rank** $r_k(i)$: its position among the distinct values of its first $k$ letters (equal
prefixes get equal ranks). The first $2k$ letters of suffix $i$ are its first $k$ letters followed by the first $k$
letters of suffix $i + k$. So comparing suffixes by their first $2k$ letters is the same as comparing the pairs

$$
\big(r_k(i), \; r_k(i + k)\big)
$$

in dictionary order, where a suffix that runs off the end gets rank $-1$ for its second half (shorter comes first).
Sorting pairs of small integers is easy: two passes of counting sort, which is radix sort from
[Chapter 6](06-Sorting-in-Linear-Time-and-Selection.md), in $O(n)$.

**Trace** on `banana`, with letter ranks a = 0, b = 1, n = 2:

| round | $k$ | pairs $(r(i), r(i+k))$ for $i = 0..5$ | sorted order | new ranks for $i = 0..5$ |
|---|---|---|---|---|
| 1 | 1 | (1,0) (0,2) (2,0) (0,2) (2,0) (0,−1) | 5, 1, 3, 0, 2, 4 | 2, 1, 3, 1, 3, 0 |
| 2 | 2 | (2,3) (1,1) (3,3) (1,0) (3,−1) (0,−1) | 5, 3, 1, 0, 4, 2 | 3, 2, 5, 1, 4, 0 |

After round 2 all six ranks differ, so the order is final: $SA = [5, 3, 1, 0, 4, 2]$, which is the table above.

**Theorem 18.8.** Prefix doubling builds the suffix array in $O(n \log n)$ time with radix sort (or $O(n \log^2 n)$ with
a comparison sort of the pairs).

*Proof.* Correctness: by induction on rounds, the ranks after the round with step $k$ order the suffixes by their first
$2k$ letters, because the pair order is exactly that order, as explained above. Once all ranks are distinct, the
order by the first $2k$ letters is a strict order of all suffixes, so it is the full sorted order. Time: after round
$t$ the prefixes compared have length $2^t$, and two different suffixes differ within their first $n$ letters, so after
at most $\lceil \log_2 n \rceil$ rounds all ranks are distinct. Each round is one radix sort of $n$ pairs of numbers
below $n$, $O(n)$. $\square$

Linear-time constructions exist. The first direct ones came in 2003 (by Kärkkäinen and Sanders, by Ko and Aluru, and
by Kim, Sim, Park and Park), and the SA-IS algorithm of Nong, Zhang and Chan (2009) is fast in practice and is what
many libraries use. They are a good deal more intricate; doubling is the one to understand first.

### The LCP array in linear time (Kasai et al. 2001)

**The question.** Computing each $LCP[j]$ by comparing letters from scratch could cost $O(n)$ each, $O(n^2)$ in all.
Kasai, Lee, Arimura, Arikawa and Park found that if we visit the suffixes in **text order** ($T[0..]$, then $T[1..]$,
then $T[2..]$, ...) rather than sorted order, the answers change slowly.

**Lemma 18.9.** Let $h$ be the LCP of suffix $i$ with the suffix just before it in sorted order. If $h > 0$, then the
LCP of suffix $i + 1$ with the suffix just before it is at least $h - 1$.

*Proof.* Let suffix $j$ be the one just before suffix $i$, so $T[j..]$ $<$ $T[i..]$ and they share the first $h \ge 1$
letters. Remove that shared first letter from both: $T[j+1..] < T[i+1..]$ and they share $h - 1$ letters. So some
suffix, namely $j + 1$, is smaller than suffix $i + 1$ and shares its first $h - 1$ letters. The suffix just before
$i + 1$ in sorted order lies between $j + 1$ and $i + 1$, and every string between two strings with a common prefix of
length $h - 1$ has that prefix too. $\square$

So keep $h$ across iterations, decrease it by one after each step, and only extend:

```python
def lcp_kasai(s, sa):
    n = len(s)
    rank = [0] * n
    for j, i in enumerate(sa):
        rank[i] = j
    lcp, h = [0] * n, 0
    for i in range(n):
        if rank[i] > 0:
            j = sa[rank[i] - 1]
            while i + h < n and j + h < n and s[i + h] == s[j + h]:
                h += 1
            lcp[rank[i]] = h
            h = max(h - 1, 0)
        else:
            h = 0
    return lcp
```

**Theorem 18.10.** Kasai's algorithm runs in $O(n)$ time.

*Proof.* $h$ starts at 0, never exceeds $n$, and decreases by at most 1 per iteration, so at most $n$ in total.
Each successful comparison increases $h$ by 1, so there are at most $n + n = 2n$ of them, plus one failed comparison per
iteration. $\square$

### What the two arrays answer

With $SA$ and $LCP$ in hand, many questions take one pass:

- **Number of distinct substrings.** Every substring is a prefix of some suffix. Suffix $SA[j]$ has $n - SA[j]$
  prefixes, of which the first $LCP[j]$ were already counted with the suffix above it. So the count is
  $\sum_j (n - SA[j] - LCP[j]) = n(n+1)/2 - \sum_j LCP[j]$. For `banana`: $21 - 6 = 15$.
- **Longest repeated substring.** Two suffixes that share the longest common prefix are next to each other in sorted
  order, so the answer has length $\max_j LCP[j]$: for `banana`, 3, the string `ana`.
- **Longest common substring of two strings** $s$ and $t$: build the arrays for $s \# t$ and take the largest $LCP[j]$
  where the two neighbouring suffixes start on different sides of $\#$ (exercise 10).
- **LCP of any two suffixes.** The LCP of the suffixes in rows $a < b$ is $\min(LCP[a+1..b])$, a range-minimum query,
  answered in $O(1)$ after a sparse table from [Chapter 10](10-Union-Find-and-Range-Queries.md).

Here is the program for 18.5 and 18.6, tested against brute force:

```python
--8<-- "books/algorithms/ch18_suffixes.py"
```

```
1. Suffix array and LCP of banana
   j  sa  lcp  suffix
   0   5    0  a
   1   3    1  ana
   2   1    3  anana
   3   0    0  banana
   4   4    0  na
   5   2    2  nana
   distinct substrings = n(n+1)/2 - sum(lcp) = 15
   longest repeated substring: 'ana'
   'ana' occurs at [1, 3]
2. Random checks against brute force
   suffix arrays, LCP counts and automaton counts agree: True
3. Burrows-Wheeler transform
   banana$       -> annb$aa       -> back: banana$
   abracadabra$  -> ard$rcaaaabb  -> back: abracadabra$
   mississippi$  -> ipssm$pissii  -> back: mississippi$
   backward search 'ssi' in mississippi: 2
   backward search 'issi' in mississippi: 2
   backward search 'ppi' in mississippi: 1
   backward search 'sip' in mississippi: 1
   backward search 'i' in mississippi: 4
4. Runs: the BWT groups equal letters
   length 189: runs in text 189, runs in BWT 29
5. Suffix automaton of banana
   states: 10  distinct substrings: 15
   contains 'nan': True  contains 'nab': False
```

The program sorts the rank pairs with Python's built-in sort, which makes each round $O(n \log n)$ and the whole
$O(n \log^2 n)$; replacing the sort with two counting-sort passes gives Theorem 18.8's bound.

**History.** Udi Manber and Gene Myers introduced suffix arrays at SODA 1990 (journal version in *SIAM Journal on
Computing*, 1993) as a space-saving alternative to suffix trees; the same structure was described independently by
Gonnet, Baeza-Yates and Snider as "PAT arrays". Kasai's LCP algorithm appeared at the Combinatorial Pattern Matching
conference in 2001.

## 18.6 Suffix trees, suffix automata and the Burrows-Wheeler transform

*Level: advanced.*

### Suffix trees

**Definition.** Put all suffixes of $T\$$ (where $\$$ is a new letter smaller than every other, so that no suffix is
a prefix of another) into a trie, then **compress** every chain of nodes with one child into a single edge labelled by
a substring. The result is the **suffix tree**. It has exactly $n + 1$ leaves, one per suffix, and every internal node
has at least two children, so it has at most $n$ internal nodes and $O(n)$ nodes in all. Edge labels are stored as
pairs of positions in $T$, not as copied strings, so the whole tree takes $O(n)$ space.

**Why it is powerful.** Each internal node is a substring that occurs at least twice and is followed by at least two
different letters (a **right-maximal repeat**). Searching for $P$ walks down from the root in $O(m)$ time (for a fixed
alphabet), and the leaves below the stopping point are exactly the occurrences. The deepest internal node, by string
length, is the longest repeated substring. The lowest common ancestor of two leaves gives the LCP of two suffixes.
In fact the suffix array is the list of leaves in left-to-right order, and the LCP array gives the string depths of
the lowest common ancestors of neighbouring leaves; either structure can be built from the other in linear time.

**Building it.** Peter Weiner gave the first linear-time construction in 1973. Edward McCreight simplified it in 1976, and Esko Ukkonen gave
an **online** construction in 1995 that adds one letter at a time from left to right, using **suffix links** (from the
node for $c\alpha$ to the node for $\alpha$, which play the role of failure links). Martin Farach (1997) gave a
linear-time construction for integer alphabets. These algorithms are linear but long; Gusfield's book gives full
proofs. In practice the constant factors matter: a suffix tree of a text of $n$ bytes typically needs 10 to 20 times
$n$ bytes of memory, which is why suffix arrays (4 or 8 bytes per letter) and the compressed indexes below replaced
them for large texts.

### Suffix automata

A different compression of the same information: the **suffix automaton** (or DAWG, directed acyclic word graph) of
$T$ is the smallest deterministic finite automaton that accepts exactly the suffixes of $T$. Reading any string from
the start state, you stay inside the automaton exactly when the string is a substring of $T$.

**What a state is.** For a substring $x$, let $\operatorname{end}(x)$ be the set of positions where an occurrence of
$x$ ends. Two substrings are equivalent when they have the same end set; each state of the automaton is one
equivalence class. In `banana` (positions 0 to 5), `an` and `n` both end at positions 2 and 4, so they are one state; `ana` and `na`
both end at 3 and 5, so they are another; `a` ends at 1, 3 and 5, so it is a third. The strings in one class are suffixes of
each other and have consecutive lengths, from $\mathrm{len}(\mathrm{link}(v)) + 1$ up to $\mathrm{len}(v)$, where the
**suffix link** $\mathrm{link}(v)$ points to the class of the longest suffix that is in a different class.

**Theorem 18.11 (Blumer, Blumer, Haussler, Ehrenfeucht, Chen, Seiferas 1985).** For $n \ge 2$ the suffix automaton
has at most $2n - 1$ states, and for $n \ge 3$ at most $3n - 4$ transitions. It can be built online in $O(n)$ time for a
fixed alphabet.

*Proof idea for the state bound.* End sets of different states are either disjoint or nested (if $y$ is a suffix of
$x$, every end of $x$ is an end of $y$), so the states form a tree under inclusion, the suffix-link tree, with the
empty string's class at the root. A child's end set is strictly smaller than its parent's. If a non-root state has
at most one child, some end position $i$ of it is in no child; that means its longest string cannot be extended to
the left at that occurrence, so it is the prefix $T[0..i]$. Each of the $n$ prefixes lies in one state, so there are
at most $n$ such states, and they include all the leaves. A tree with at most $n$ leaves has at most $n - 1$ nodes with
two or more children. Together that is at most $2n - 1$ (the root needs a separate, easy check). The transition bound and the linear-time construction are
proved in the 1985 paper and in Crochemore, Hancart and Lecroq's book. $\square$

The construction in the program adds one letter $c$ at a time. It creates a state for the whole new prefix, walks up
the suffix links adding transitions on $c$ until one already exists, and, when the existing target is "too long" for
the new class, **clones** it to split the class. The number of distinct substrings is then
$\sum_v (\mathrm{len}(v) - \mathrm{len}(\mathrm{link}(v)))$, since each state holds exactly that many strings. The
program checks it against brute force on 300 random strings, and gets 15 for `banana` with 10 states.

### The Burrows-Wheeler transform

**The question.** Can an index be *smaller* than the text? The Burrows-Wheeler transform (BWT) is a reversible
permutation of the text's letters that tends to group equal letters together, which makes it easy to compress, and that
also supports pattern search. It is the base of the bzip2 compressor and of the read aligners that map DNA sequencing
data to a reference genome.

**Definition.** Append $\$$ to $T$. Write all $n + 1$ cyclic rotations of $T\$$, sort them, and read off the **last
column** $L$. The first column $F$ is just the letters of $T\$$ in sorted order. Because $\$$ is unique and smallest,
sorting rotations is the same as sorting suffixes, so $L[j] = T[SA[j] - 1]$ (the letter just before each suffix, with
$T[-1] = \$$).

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 420 300" role="img" aria-label="The Burrows-Wheeler matrix of banana dollar. Seven sorted rotations in rows. The first column F reads dollar a a a b n n, the last column L reads a n n b dollar a a. Small numbers count the a letters in each column.">
<text x="40" y="28" font-size="13" text-anchor="middle" fill="currentColor">row</text>
<text x="100" y="28" font-size="13" text-anchor="middle" fill="currentColor">F</text>
<text x="280" y="28" font-size="13" text-anchor="middle" fill="currentColor">L</text>
<text x="370" y="28" font-size="13" text-anchor="middle" fill="currentColor">SA</text>
<rect x="85" y="38" width="30" height="245" fill="#9cc9ea" fill-opacity="0.45"/>
<rect x="265" y="38" width="30" height="245" fill="#eea66f" fill-opacity="0.45"/>
<g font-size="16" font-family="monospace" text-anchor="middle" fill="currentColor">
<text x="40" y="62">0</text><text x="100" y="62">$</text><text x="130" y="62">b</text><text x="160" y="62">a</text><text x="190" y="62">n</text><text x="220" y="62">a</text><text x="250" y="62">n</text><text x="280" y="62">a</text><text x="370" y="62">6</text>
<text x="40" y="97">1</text><text x="100" y="97">a</text><text x="130" y="97">$</text><text x="160" y="97">b</text><text x="190" y="97">a</text><text x="220" y="97">n</text><text x="250" y="97">a</text><text x="280" y="97">n</text><text x="370" y="97">5</text>
<text x="40" y="132">2</text><text x="100" y="132">a</text><text x="130" y="132">n</text><text x="160" y="132">a</text><text x="190" y="132">$</text><text x="220" y="132">b</text><text x="250" y="132">a</text><text x="280" y="132">n</text><text x="370" y="132">3</text>
<text x="40" y="167">3</text><text x="100" y="167">a</text><text x="130" y="167">n</text><text x="160" y="167">a</text><text x="190" y="167">n</text><text x="220" y="167">a</text><text x="250" y="167">$</text><text x="280" y="167">b</text><text x="370" y="167">1</text>
<text x="40" y="202">4</text><text x="100" y="202">b</text><text x="130" y="202">a</text><text x="160" y="202">n</text><text x="190" y="202">a</text><text x="220" y="202">n</text><text x="250" y="202">a</text><text x="280" y="202">$</text><text x="370" y="202">0</text>
<text x="40" y="237">5</text><text x="100" y="237">n</text><text x="130" y="237">a</text><text x="160" y="237">$</text><text x="190" y="237">b</text><text x="220" y="237">a</text><text x="250" y="237">n</text><text x="280" y="237">a</text><text x="370" y="237">4</text>
<text x="40" y="272">6</text><text x="100" y="272">n</text><text x="130" y="272">a</text><text x="160" y="272">n</text><text x="190" y="272">a</text><text x="220" y="272">$</text><text x="250" y="272">b</text><text x="280" y="272">a</text><text x="370" y="272">2</text>
</g>
<g font-size="10" fill="currentColor">
<text x="107" y="101">1</text><text x="107" y="136">2</text><text x="107" y="171">3</text>
<text x="287" y="66">1</text><text x="287" y="241">2</text><text x="287" y="276">3</text>
</g>
</svg>
<figcaption>Figure 18.4. The sorted rotations of banana$. The first column F (blue) is the sorted letters; the last column L (orange), annb$aa, is the Burrows-Wheeler transform. The LF mapping: the k-th occurrence of a letter in L is the same text letter as the k-th occurrence of that letter in F. SA gives the start of each row's suffix.</figcaption>
</figure>

For `banana` the transform is `annb$aa`. For a longer English-like text the effect is striking: in the program a
189-letter text with 189 runs of equal letters (no two neighbours equal) has a BWT with only 29 runs. The reason: rows
are sorted by what *follows* each last-column letter, so letters that precede the same context, like the letters
before `he_` in English, end up next to each other, and those are usually the same letter (`t`).

**Why it can be undone: the LF mapping.** Take any letter $c$. The rows that *start* with $c$ are sorted by what comes
after that $c$. The rows that *end* with $c$ are the same rotations turned by one position, and they are sorted by what
comes after the $c$ as well (since the row starts right after it). So the order of the $c$'s is the same in both
columns:

**Lemma 18.12 (LF mapping).** The $k$-th occurrence of letter $c$ in $L$ and the $k$-th occurrence of $c$ in $F$ are
the same letter of the text.

So if row $j$ ends with $c = L[j]$, and this is the $k$-th $c$ in $L$, then the rotation that starts with that very $c$
is row $LF(j) = C[c] + k - 1$, where $C[c]$ is the number of letters in the text smaller than $c$ (the first row starting
with $c$). Starting from row 0 (which begins with $\$$), $L[0]$ is the last text letter; jump to $LF(0)$ and read the
letter before it; and so on. Each jump steps one letter **backwards** through the text, and after $n + 1$ jumps the
whole text has been recovered. With the counts precomputed, inversion takes $O(n)$ time.

**Trace** of inversion for `annb$aa`. $C$: $\$ \to 0$, a $\to 1$, b $\to 4$, n $\to 5$. Row 0: $L[0]$ = a, the 1st a
in $L$, so go to row $1 + 0 = 1$. $L[1]$ = n, 1st n, row 5. $L[5]$ = a, 2nd a, row 2. $L[2]$ = n, 2nd n, row 6.
$L[6]$ = a, 3rd a, row 3. $L[3]$ = b, row 4. $L[4] = \$$, done. Letters read: a, n, a, n, a, b, which backwards is
`banana`.

**Searching without the text: backward search.** Ferragina and Manzini (2000) saw that the LF mapping also searches.
Keep the interval $[lo, hi)$ of rows that start with a suffix of the pattern, beginning with the empty suffix (all rows),
and extend it to the left one pattern letter at a time. If the rows in $[lo, hi)$ start with $\alpha$, the rows that
start with $c\alpha$ are the images under LF of the rows in $[lo, hi)$ whose last letter is $c$, and LF keeps their
order. So

$$
lo' = C[c] + \mathrm{occ}(c, lo), \qquad hi' = C[c] + \mathrm{occ}(c, hi),
$$

where $\mathrm{occ}(c, i)$ is the number of $c$'s in $L[0..i-1]$. **Trace** for `ana` in `annb$aa`: start with
$[0, 7)$. Letter a: $[1 + 0, 1 + 3) = [1, 4)$, the rows starting with a. Letter n: $[5 + \mathrm{occ}(n, 1), 5 +
\mathrm{occ}(n, 4)) = [5, 7)$, rows starting with na. Letter a: $[1 + \mathrm{occ}(a, 5), 1 + \mathrm{occ}(a, 7)) = [2,
4)$: two rows, so `ana` occurs twice.

**The FM-index.** If $\mathrm{occ}$ is stored for every $i$ it takes as much space as a suffix array. Instead store it
every 64 or 128 positions and count the rest with bit tricks, keep $L$ compressed, and keep a sample of the suffix array
to turn rows into text positions. The result, the **FM-index**, counts occurrences of $P$ in $O(m)$ time (for a small
alphabet) while using space close to the compressed size of the text. The human genome, about 3.1 billion letters,
fits in a few gigabytes this way. The aligners Bowtie (Langmead, Trapnell, Pop and Salzberg, 2009) and BWA (Li and
Durbin, 2009) are built on it, and they made it practical to map the hundreds of millions of short reads from one
sequencing run.

**Compression.** Michael Burrows and David Wheeler described the transform in 1994 in a research report of the Digital
Systems Research Center, "A Block-sorting Lossless Data Compression Algorithm" (Wheeler had found the transform years
earlier). After the BWT, a **move-to-front** step turns runs of equal letters into runs of small numbers, and a Huffman
coder ([Chapter 12](12-Greedy-Algorithms.md)) or arithmetic coder compresses them. Julian Seward's bzip2 compressor,
released in 1996, works this way on blocks of up to 900 kB.

### In practice

Python's `str.find` and `in` use a tuned mix of a simplified Boyer-Moore-Horspool search and, since Python 3.10, the
"two-way" algorithm of Crochemore and Perrin (1991) for longer patterns, which is linear in the worst case with $O(1)$
extra space. **Boyer-Moore** (1977), which compares the pattern from right to left and can skip ahead by up to $m$
letters, is the classic choice for long patterns on large alphabets: on English text it reads only a fraction of the
letters. `grep` uses Boyer-Moore-style skipping for fixed strings. Regular expressions are compiled to automata, the
general form of what Aho-Corasick builds. For indexes, libraries such as `libdivsufsort` build suffix arrays, and the
`sdsl-lite` library provides FM-indexes and other succinct structures.

## Check yourself

??? question "1. Compute the prefix function of `aabaaab` by hand."

    $\pi = [0, 1, 0, 1, 2, 2, 3]$. Steps: $\pi[1] = 1$ (a = a). At $i = 2$ (b), $k = 1$: b $\neq P[1] =$ a, fall to
    $\pi[0] = 0$, b $\neq$ a, so 0. $i = 3$ (a): match $P[0]$, 1. $i = 4$ (a): match $P[1]$, 2. $i = 5$ (a): $P[2]$ = b
    $\neq$ a, fall to $k = \pi[1] = 1$, $P[1]$ = a matches, so 2. $i = 6$ (b): $P[2]$ = b matches, 3.

??? question "2. How many letter comparisons does the naive method make on $T = \texttt{a}^{20}$ and $P = \texttt{aaab}$? What about $P = \texttt{baaa}$?"

    For `aaab` every one of the $20 - 4 + 1 = 17$ shifts compares 4 letters: $68$ comparisons. For `baaa` every
    shift fails at the first letter: 17 comparisons. The worst case depends on where in the pattern the mismatch
    comes; a pattern whose mismatch is at the end is the bad one for left-to-right comparison.

??? question "3. Compute the Z-array of `abacaba` and use it to find every position where a prefix of length 3 reappears."

    $Z = [7, 0, 1, 0, 3, 0, 1]$. $Z[i] \ge 3$ only at $i = 4$ (besides $i = 0$), so `aba` reappears at position 4.

??? question "4. Show that the smallest period of `abcabcab` is 3 using the prefix function. When is a string a power $u^k$ of a shorter string?"

    $\pi = [0, 0, 0, 1, 2, 3, 4, 5]$, so the longest border has length 5 and the smallest period is $8 - 5 = 3$. A
    string of length $n$ is $u^k$ with $k \ge 2$ exactly when its smallest period $p = n - \pi[n-1]$ divides $n$ and
    $p < n$. Here $3$ does not divide 8, so `abcabcab` is not a power; `abcabc` (period 3, length 6) is $(\texttt{abc})^2$.
    (That the smallest period must divide $n$ when any proper divisor period exists follows from the periodicity
    lemma of Fine and Wilf.)

??? question "5. Write a function that counts the occurrences of a pattern with KMP using only the prefix function of $P\#T$."

    Every position $i$ in the $T$ part with $\pi[i] = m$ is the end of an occurrence (the separator stops borders
    from being longer than $m$):

    ```python
    def count_kmp(text, pat):
        s = pat + "\0" + text
        pi = [0] * len(s)
        k = 0
        for i in range(1, len(s)):
            while k and s[i] != s[k]:
                k = pi[k - 1]
            if s[i] == s[k]:
                k += 1
            pi[i] = k
        return sum(1 for v in pi[len(pat) + 1:] if v == len(pat))

    print(count_kmp("abababa", "aba"))   # 3
    ```

??? question "6. In the Rabin-Karp example of 18.3 ($b = 10$, $p = 13$), check that the window at shift 12 is a spurious hit. What is the probability bound of Theorem 18.6 for $m = 5$ and $p = 13$, and why is the example not covered by it?"

    $67399 = 5184 \times 13 + 7$, so it hashes to 7 like $31415 = 2416 \times 13 + 7$, but the strings differ. Theorem
    18.6 gives at most $4/13$ per pair, a weak bound because $p$ is tiny; and it applies only when the base is
    random, while here $b = 10$ is fixed. With a fixed base, an adversary who knows $b$ and $p$ can make collisions
    on purpose.

??? question "7. Build the failure links for the patterns `a`, `ab`, `bab`, `bc`. Which patterns are reported when the automaton reads `babc`?"

    Trie states: 0 root, 1 a, 2 ab, 3 b, 4 ba, 5 bab, 6 bc. Failure links: a, b fail to 0; ab fails to b (3); ba
    fails to a (1); bab fails to ab (2); bc fails to 0. Reading `babc`: b → 3; a → 4 (ba), output link to a, report
    `a`; b → 5 (bab), report `bab`, output link to 2 (ab), report `ab`; c: state 5 has no c, fail to 2, which has no c,
    fail to 3 (b), which has c → 6, report `bc`. Reported: a at 1, bab at 0, ab at 1, bc at 2.

??? question "8. Build the suffix array and LCP array of `mississippi`, and use them to find the number of distinct substrings and the longest repeated substring."

    $SA = [10, 7, 4, 1, 0, 9, 8, 6, 3, 5, 2]$ (suffixes i, ippi, issippi, ississippi, mississippi, pi, ppi, sippi,
    sissippi, ssippi, ssissippi) and $LCP = [0, 1, 1, 4, 0, 0, 1, 0, 2, 1, 3]$. Distinct substrings: $66 - 13 = 53$.
    Longest repeated: length 4 at row 3, `issi` (it occurs at positions 1 and 4, overlapping).

??? question "9. Invert the Burrows-Wheeler transform `ard$rcaaaabb` by hand, at least for the first five steps."

    Counts: `$` 1, a 5, b 2, c 1, d 1, r 2, so $C$: $\$ \to 0$, a $\to 1$, b $\to 6$, c $\to 8$, d $\to 9$, r $\to 10$.
    Row 0: $L[0]$ = a (1st a) → row 1. $L[1]$ = r (1st r) → row 10. $L[10]$ = b (1st b) → row 6. $L[6]$ = a (2nd a)
    → row 2. $L[2]$ = d → row 9. Letters so far: a, r, b, a, d, which backwards is the end `...dabra`. Continuing
    gives `abracadabra`.

??? question "10. Write code for the longest common substring of two strings using a suffix array."

    Join with a separator smaller than all letters and look at neighbouring suffixes from different sides:

    ```python
    def longest_common_substring(s, t):
        u = s + "\x01" + t
        sa = sorted(range(len(u)), key=lambda i: u[i:])      # fine for small inputs
        best, where = 0, 0
        for j in range(1, len(u)):
            a, b = sa[j - 1], sa[j]
            if (a < len(s)) != (b < len(s)):                  # one from s, one from t
                h = 0
                while a + h < len(u) and b + h < len(u) and u[a + h] == u[b + h] != "\x01":
                    h += 1
                if h > best:
                    best, where = h, b
        return u[where:where + best]

    print(longest_common_substring("algorithm", "rhythm"))   # 'thm'
    ```

    It works because the longest common substring is a common prefix of a suffix of $s$ and a suffix of $t$, and the
    pair with the longest common prefix of that kind is adjacent in sorted order or separated only by suffixes that
    share at least as long a prefix, one of which is from the other side. For large inputs use `suffix_array` and
    `lcp_kasai` from the chapter's program instead of the slow sort.

??? question "11. Prove that any algorithm that finds every occurrence of the pattern `a` in a text of length $n$ must read all $n$ letters in the worst case."

    Adversary argument. Suppose an algorithm stops without reading position $i$. Answer every read with `b`. If the
    algorithm reports no match, set $T[i]$ = a; if it reports a match at $i$, set $T[i]$ = b. Either way its output
    is wrong for a text consistent with everything it read. So it must read every position. For longer patterns
    Boyer-Moore can skip letters, but Rivest (1977) showed that in the worst case any algorithm must examine at least
    $n - m + 1$ text letters.

??? question "12. Why does the suffix automaton of `abab` have 5 states? List the states as classes of substrings."

    End sets (positions 0 to 3): {a, ...}: `a` ends at {0, 2}; `b`, `ab` end at {1, 3}; `aba`, `ba` end at {2}; `abab`,
    `bab` end at {3}. With the start state (empty string) that is 5 states: $\{\varepsilon\}$, $\{a\}$, $\{b, ab\}$,
    $\{ba, aba\}$, $\{bab, abab\}$. They hold $1 + 2 + 2 + 2 = 7$ non-empty substrings, matching
    $n(n+1)/2 - \sum LCP = 10 - 3 = 7$.

## What you learned

- The naive search costs $(n - m + 1)m$ comparisons in the worst case; every faster method avoids re-reading text
  it already knows.
- The prefix function lists the borders of each prefix; KMP uses it to search in at most $2n$ comparisons, proved by
  a potential argument on $k$.
- The Z-algorithm finds every reoccurrence of the prefix in linear time by reusing its rightmost box.
- A rolling hash with a random base collides with probability at most $(m-1)/p$, which makes Rabin-Karp fast in
  expectation and flexible for many patterns and repeated substrings.
- A trie with failure and output links, the Aho-Corasick automaton, finds all occurrences of many patterns in
  $O(n + z)$ after $O(M)$ preprocessing.
- Suffix arrays (prefix doubling, $O(n \log n)$) with LCP arrays (Kasai, $O(n)$) index a fixed text: searches in
  $O(m \log n)$, distinct substrings, longest repeats.
- Suffix trees and suffix automata do the same in linear size; the Burrows-Wheeler transform and the LF mapping give
  compressed indexes (the FM-index) and the bzip2 compressor.

**Next:** [Chapter 19](19-Number-Theoretic-Algorithms.md), algorithms on whole numbers: gcds, fast powers, primality
tests, factoring and the number-theoretic transform.

## Further reading

- D. E. Knuth, J. H. Morris and V. R. Pratt, "Fast Pattern Matching in Strings", *SIAM Journal on Computing* 6(2), 1977.
- R. M. Karp and M. O. Rabin, "Efficient Randomized Pattern-Matching Algorithms", *IBM Journal of Research and Development* 31(2), 1987.
- A. V. Aho and M. J. Corasick, "Efficient String Matching: An Aid to Bibliographic Search", *Communications of the ACM* 18(6), 1975.
- R. S. Boyer and J S. Moore, "A Fast String Searching Algorithm", *Communications of the ACM* 20(10), 1977.
- U. Manber and G. Myers, "Suffix Arrays: A New Method for On-Line String Searches", *SIAM Journal on Computing* 22(5), 1993.
- T. Kasai, G. Lee, H. Arimura, S. Arikawa and K. Park, "Linear-Time Longest-Common-Prefix Computation in Suffix Arrays and Its Applications", CPM 2001.
- E. Ukkonen, "On-Line Construction of Suffix Trees", *Algorithmica* 14, 1995.
- A. Blumer, J. Blumer, D. Haussler, A. Ehrenfeucht, M. T. Chen and J. Seiferas, "The Smallest Automaton Recognizing the Subwords of a Text", *Theoretical Computer Science* 40, 1985.
- M. Burrows and D. J. Wheeler, "A Block-sorting Lossless Data Compression Algorithm", Digital SRC Research Report 124, 1994.
- P. Ferragina and G. Manzini, "Opportunistic Data Structures with Applications", FOCS 2000.
- G. Nong, S. Zhang and W. H. Chan, "Linear Suffix Array Construction by Almost Pure Induced-Sorting", DCC 2009.
- D. Gusfield, *Algorithms on Strings, Trees, and Sequences*, 1997: the standard book, with full proofs of the suffix-tree constructions.
- M. Crochemore, C. Hancart and T. Lecroq, *Algorithms on Strings*, 2007.
- CLRS (Cormen, Leiserson, Rivest, Stein, *Introduction to Algorithms*, 4th ed. 2022), chapter 32; Sedgewick and Wayne (*Algorithms*, 4th ed. 2011), chapter 5.
- On this site: [Knuth-Morris-Pratt](../../strings/kmp.md), [Z-algorithm](../../strings/z-algorithm.md),
  [Rabin-Karp](../../strings/rabin-karp.md), [Trie](../../data-structures/trie.md), and
  [Chapter 13](13-Dynamic-Programming.md) for edit distance and LCS, the other half of string algorithms.
