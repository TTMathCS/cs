"""Chapter 18: suffix arrays, the LCP array, the Burrows-Wheeler transform,
backward search (the heart of the FM-index) and the suffix automaton."""
import random


def suffix_array(s):
    """Prefix doubling: sort suffixes by their first 1, 2, 4, ... letters.
    Each round sorts pairs of ranks; with Python's sort this is O(n log^2 n),
    with radix sort on the pairs it is O(n log n)."""
    n = len(s)
    rank = [ord(c) for c in s]
    sa = list(range(n))
    k = 1
    while True:
        key = lambda i: (rank[i], rank[i + k] if i + k < n else -1)
        sa.sort(key=key)
        new = [0] * n
        for j in range(1, n):
            new[sa[j]] = new[sa[j - 1]] + (key(sa[j]) != key(sa[j - 1]))
        rank = new
        if rank[sa[-1]] == n - 1:   # all ranks distinct: fully sorted
            return sa
        k *= 2


def lcp_kasai(s, sa):
    """lcp[j] = longest common prefix of suffixes sa[j-1] and sa[j]; lcp[0] = 0."""
    n = len(s)
    rank = [0] * n
    for j, i in enumerate(sa):
        rank[i] = j
    lcp = [0] * n
    h = 0
    for i in range(n):              # suffixes in text order: s[0:], s[1:], ...
        if rank[i] > 0:
            j = sa[rank[i] - 1]     # the suffix just before s[i:] in sorted order
            while i + h < n and j + h < n and s[i + h] == s[j + h]:
                h += 1
            lcp[rank[i]] = h
            if h:
                h -= 1              # the key fact: drop by at most one
        else:
            h = 0
    return lcp


def find_all(s, sa, pat):
    """Binary search for the block of suffixes that start with pat."""
    m = len(pat)
    lo, hi = 0, len(sa)
    while lo < hi:
        mid = (lo + hi) // 2
        if s[sa[mid]:sa[mid] + m] < pat:
            lo = mid + 1
        else:
            hi = mid
    start, hi = lo, len(sa)
    while lo < hi:
        mid = (lo + hi) // 2
        if s[sa[mid]:sa[mid] + m] <= pat:
            lo = mid + 1
        else:
            hi = mid
    return sorted(sa[start:lo])


def bwt(s):
    """s must end with a unique smallest letter '$'."""
    sa = suffix_array(s)
    return "".join(s[i - 1] for i in sa)     # s[-1] is '$' when i = 0


def inverse_bwt(last):
    """LF mapping: the k-th c in the last column is the k-th c in the first."""
    n = len(last)
    counts, occ_before = {}, []
    for c in last:
        occ_before.append(counts.get(c, 0))
        counts[c] = counts.get(c, 0) + 1
    first_pos, total = {}, 0
    for c in sorted(counts):
        first_pos[c] = total
        total += counts[c]
    row, out = 0, []                 # row 0 starts with '$'
    for _ in range(n):
        c = last[row]
        out.append(c)
        row = first_pos[c] + occ_before[row]
    out.reverse()                    # we walked backwards through the text
    return "".join(out[1:]) + out[0]


def backward_search(last, pat):
    """How many times pat occurs, using only the BWT (the FM-index idea)."""
    C, total = {}, 0
    for c in sorted(set(last)):
        C[c] = total
        total += last.count(c)

    def occ(c, i):                   # occurrences of c in last[0:i]
        return last[:i].count(c)     # a real FM-index stores these in samples

    lo, hi = 0, len(last)
    for c in reversed(pat):
        if c not in C:
            return 0
        lo, hi = C[c] + occ(c, lo), C[c] + occ(c, hi)
        if lo >= hi:
            return 0
    return hi - lo


class SuffixAutomaton:
    """Blumer et al. 1985; the online construction adds one letter at a time."""

    def __init__(self, s):
        self.next, self.link, self.len = [{}], [-1], [0]
        last = 0
        for c in s:
            cur = len(self.len)
            self.next.append({}); self.link.append(0); self.len.append(self.len[last] + 1)
            p = last
            while p != -1 and c not in self.next[p]:
                self.next[p][c] = cur
                p = self.link[p]
            if p != -1:
                q = self.next[p][c]
                if self.len[p] + 1 == self.len[q]:
                    self.link[cur] = q
                else:                # split q: clone keeps the shorter strings
                    clone = len(self.len)
                    self.next.append(dict(self.next[q]))
                    self.link.append(self.link[q])
                    self.len.append(self.len[p] + 1)
                    while p != -1 and self.next[p].get(c) == q:
                        self.next[p][c] = clone
                        p = self.link[p]
                    self.link[q] = self.link[cur] = clone
            last = cur

    def distinct_substrings(self):
        return sum(self.len[v] - self.len[self.link[v]] for v in range(1, len(self.len)))

    def contains(self, t):
        v = 0
        for c in t:
            if c not in self.next[v]:
                return False
            v = self.next[v][c]
        return True


def main():
    s = "banana"
    sa = suffix_array(s)
    lcp = lcp_kasai(s, sa)
    print("1. Suffix array and LCP of", s)
    print("   j  sa  lcp  suffix")
    for j, (i, h) in enumerate(zip(sa, lcp)):
        print(f"   {j}  {i:2d}  {h:3d}  {s[i:]}")
    n = len(s)
    print("   distinct substrings = n(n+1)/2 - sum(lcp) =", n * (n + 1) // 2 - sum(lcp))
    j = max(range(n), key=lambda j: lcp[j])
    print("   longest repeated substring:", repr(s[sa[j]:sa[j] + lcp[j]]))
    print("   'ana' occurs at", find_all(s, sa, "ana"))

    print("2. Random checks against brute force")
    rng = random.Random(18)
    ok = True
    for _ in range(300):
        t = "".join(rng.choice("abc") for _ in range(rng.randint(1, 30)))
        sa_t = suffix_array(t)
        ok &= sa_t == sorted(range(len(t)), key=lambda i: t[i:])
        lc = lcp_kasai(t, sa_t)
        brute = len({t[i:j] for i in range(len(t)) for j in range(i + 1, len(t) + 1)})
        ok &= len(t) * (len(t) + 1) // 2 - sum(lc) == brute
        ok &= SuffixAutomaton(t).distinct_substrings() == brute
    print("   suffix arrays, LCP counts and automaton counts agree:", ok)

    print("3. Burrows-Wheeler transform")
    for word in ("banana$", "abracadabra$", "mississippi$"):
        b = bwt(word)
        print(f"   {word:13s} -> {b:13s} -> back: {inverse_bwt(b)}")
    b = bwt("mississippi$")
    for pat in ("ssi", "issi", "ppi", "sip", "i"):
        print(f"   backward search '{pat}' in mississippi: {backward_search(b, pat)}")

    print("4. Runs: the BWT groups equal letters")
    text = ("the cat sat on the mat and the cat ate the rat " * 4).replace(" ", "_") + "$"
    b = bwt(text)
    runs = lambda x: 1 + sum(x[i] != x[i - 1] for i in range(1, len(x)))
    print(f"   length {len(text)}: runs in text {runs(text)}, runs in BWT {runs(b)}")

    print("5. Suffix automaton of", s)
    sam = SuffixAutomaton(s)
    print("   states:", len(sam.len), " distinct substrings:", sam.distinct_substrings())
    print("   contains 'nan':", sam.contains("nan"), " contains 'nab':", sam.contains("nab"))


if __name__ == "__main__":
    main()
