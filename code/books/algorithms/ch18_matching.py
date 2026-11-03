"""Chapter 18: matching one pattern, or many, in a text.

Naive matching, the KMP prefix function, the Z-function, Rabin-Karp and
Aho-Corasick, each built from scratch and checked against the naive answer.
"""
import random
from collections import deque


def naive(text, pat):
    """Every start where pat occurs, plus the number of letter comparisons."""
    n, m = len(text), len(pat)
    found, comps = [], 0
    for s in range(n - m + 1):
        j = 0
        while j < m:
            comps += 1
            if text[s + j] != pat[j]:
                break
            j += 1
        if j == m:
            found.append(s)
    return found, comps


def prefix_function(p):
    """pi[i] = length of the longest proper border of p[0..i]."""
    pi = [0] * len(p)
    k = 0
    for i in range(1, len(p)):
        while k > 0 and p[i] != p[k]:
            k = pi[k - 1]          # fall back to the next shorter border
        if p[i] == p[k]:
            k += 1
        pi[i] = k
    return pi


def kmp(text, pat):
    """Every start of pat in text, plus the number of letter comparisons."""
    pi = prefix_function(pat)
    found, comps, k = [], 0, 0
    for i, c in enumerate(text):
        while True:
            comps += 1
            if c == pat[k]:
                k += 1
                break
            if k == 0:
                break
            k = pi[k - 1]
        if k == len(pat):
            found.append(i - k + 1)
            k = pi[k - 1]
    return found, comps


def z_function(s):
    """z[i] = length of the longest common prefix of s and s[i:]; z[0] = len(s)."""
    n = len(s)
    z = [0] * n
    if n:
        z[0] = n
    left = right = 0                # [left, right) is the rightmost Z-box seen
    for i in range(1, n):
        if i < right:
            z[i] = min(right - i, z[i - left])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] > right:
            left, right = i, i + z[i]
    return z


def z_search(text, pat, sep="\0"):
    z = z_function(pat + sep + text)
    m = len(pat)
    return [i - m - 1 for i in range(m + 1, len(z)) if z[i] >= m]


def rabin_karp(text, pat, base=256, mod=1_000_000_007):
    """Rolling-hash search. Returns matches and how many hash hits were false."""
    n, m = len(text), len(pat)
    if m > n:
        return [], 0
    high = pow(base, m - 1, mod)    # weight of the letter that leaves the window
    hp = ht = 0
    for i in range(m):
        hp = (hp * base + ord(pat[i])) % mod
        ht = (ht * base + ord(text[i])) % mod
    found, false_hits = [], 0
    for s in range(n - m + 1):
        if hp == ht:
            if text[s:s + m] == pat:   # always check: equal hashes may be a collision
                found.append(s)
            else:
                false_hits += 1
        if s + m < n:
            ht = ((ht - ord(text[s]) * high) * base + ord(text[s + m])) % mod
    return found, false_hits


class AhoCorasick:
    """A trie of the patterns with failure links and output links."""

    def __init__(self, patterns):
        self.goto = [{}]            # goto[state][letter] -> state
        self.fail = [0]
        self.out = [[]]             # patterns that end exactly at this state
        self.patterns = patterns
        for idx, p in enumerate(patterns):
            s = 0
            for c in p:
                if c not in self.goto[s]:
                    self.goto.append({})
                    self.fail.append(0)
                    self.out.append([])
                    self.goto[s][c] = len(self.goto) - 1
                s = self.goto[s][c]
            self.out[s].append(idx)
        self.dict_link = [0] * len(self.goto)   # nearest proper suffix state with output
        queue = deque(self.goto[0].values())    # depth-1 states fail to the root
        while queue:                            # breadth first: shorter strings first
            r = queue.popleft()
            for c, u in self.goto[r].items():
                queue.append(u)
                f = self.fail[r]
                while f and c not in self.goto[f]:
                    f = self.fail[f]
                self.fail[u] = self.goto[f].get(c, 0)
                g = self.fail[u]
                self.dict_link[u] = g if self.out[g] else self.dict_link[g]

    def search(self, text):
        s, hits = 0, []
        for i, c in enumerate(text):
            while s and c not in self.goto[s]:
                s = self.fail[s]
            s = self.goto[s].get(c, 0)
            t = s
            while t:
                for idx in self.out[t]:
                    hits.append((i - len(self.patterns[idx]) + 1, self.patterns[idx]))
                t = self.dict_link[t]
        return sorted(hits)


def main():
    print("1. Naive matching, worst case")
    for n in (100, 1000, 10000):
        text, pat = "a" * n, "a" * 49 + "b"
        _, c1 = naive(text, pat)
        _, c2 = kmp(text, pat)
        print(f"   n={n:6d} m=50: naive {c1:7d} comparisons, KMP {c2:6d}")

    print("2. Prefix function")
    for p in ("ABABCABAB", "aabaaab", "abacaba"):
        print("  ", p, prefix_function(p))

    print("3. Z-function")
    for s in ("aabxaab", "abacaba"):
        print("  ", s, z_function(s))

    text = "ABABDABACDABABCABABABABCABAB"
    pat = "ABABCABAB"
    print("4. Same answers from four methods on", text)
    print("   naive      ", naive(text, pat)[0])
    print("   KMP        ", kmp(text, pat)[0])
    print("   Z          ", z_search(text, pat))
    print("   Rabin-Karp ", rabin_karp(text, pat)[0])

    print("5. Random tests against naive")
    rng = random.Random(18)
    ok = True
    for _ in range(2000):
        t = "".join(rng.choice("ab") for _ in range(rng.randint(1, 40)))
        p = "".join(rng.choice("ab") for _ in range(rng.randint(1, 5)))
        want = naive(t, p)[0]
        ok &= kmp(t, p)[0] == want == z_search(t, p) == rabin_karp(t, p)[0]
    print("   2000 random cases agree:", ok)

    print("6. Rabin-Karp with a tiny modulus shows collisions")
    t = "".join(rng.choice("abcd") for _ in range(10000))
    for mod in (101, 10007, 1_000_000_007):
        found, false_hits = rabin_karp(t, "abcab", mod=mod)
        print(f"   mod={mod:>10}: {len(found)} matches, {false_hits} false hash hits")

    print("7. Aho-Corasick")
    ac = AhoCorasick(["he", "she", "his", "hers"])
    print("   fail links:", ac.fail)
    print("   'ushers' ->", ac.search("ushers"))
    print("   'ahishers' ->", ac.search("ahishers"))


if __name__ == "__main__":
    main()
