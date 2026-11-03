# Chapter 16: a small probabilistic context-free grammar (PCFG) that generates the toy corpus
# used by the other Chapter 16 programs. Every generated sentence comes with its part-of-speech
# tags and its parse tree, so we know the right answers. Imported by the other programs;
# run on its own, it prints samples and statistics.
import random
from collections import Counter

# Nonterminal rules (all binary) and lexical rules (one word), with probabilities summing to 1
# for each left-hand side. This is Chomsky normal form, which the CKY parser needs.
RULES = {
    "S":   [(("NP", "VP"), 1.0)],
    "NP":  [(("Det", "N"), 0.55), (("Det", "AN"), 0.20), (("NP", "PP"), 0.15), ("ada", 0.05), ("ben", 0.05)],
    "AN":  [(("Adj", "N"), 1.0)],
    "VP":  [(("V", "NP"), 0.55), (("VP", "PP"), 0.20), ("stops", 0.08), ("waits", 0.07), ("turns", 0.05),
            ("rolls", 0.05)],
    "PP":  [(("P", "NP"), 1.0)],
    "Det": [("the", 0.7), ("a", 0.3)],
    "Adj": [("red", 0.3), ("small", 0.25), ("dusty", 0.2), ("old", 0.15), ("bright", 0.1)],
    "N":   [("rover", 0.22), ("rock", 0.18), ("crater", 0.12), ("camera", 0.09), ("dune", 0.08),
            ("scientist", 0.07), ("robot", 0.06), ("ridge", 0.05), ("drills", 0.04), ("tracks", 0.04),
            ("samples", 0.03), ("wheel", 0.02)],
    "V":   [("sees", 0.25), ("drills", 0.18), ("finds", 0.15), ("tracks", 0.12), ("photographs", 0.1),
            ("samples", 0.08), ("follows", 0.07), ("studies", 0.05)],
    "P":   [("with", 0.4), ("near", 0.3), ("on", 0.2), ("behind", 0.1)],
}
# the part-of-speech tag of a word produced directly by a nonterminal
TAG_OF = {"NP": "NAME", "VP": "V", "Det": "DET", "Adj": "ADJ", "N": "N", "V": "V", "P": "P"}


def generate(rng, symbol="S", depth=0):
    """Return (words, tags, tree) for a random expansion of symbol."""
    options = RULES[symbol]
    if depth > 12:                                   # keep sentences short: forbid recursion when deep
        options = [o for o in options if not (isinstance(o[0], tuple) and symbol in o[0])] or options
    total = sum(p for _, p in options)
    x, acc = rng.random() * total, 0.0
    for rhs, p in options:
        acc += p
        if x <= acc:
            break
    if isinstance(rhs, str):
        return [rhs], [TAG_OF[symbol]], (symbol, rhs)
    w1, t1, tr1 = generate(rng, rhs[0], depth + 1)
    w2, t2, tr2 = generate(rng, rhs[1], depth + 1)
    return w1 + w2, t1 + t2, (symbol, tr1, tr2)


def corpus(n, seed):
    rng = random.Random(seed)
    return [generate(rng) for _ in range(n)]


def show_tree(tree):
    if isinstance(tree[1], str):
        return f"({tree[0]} {tree[1]})"
    return f"({tree[0]} {show_tree(tree[1])} {show_tree(tree[2])})"


if __name__ == "__main__":
    data = corpus(5000, 16)
    for words, tags, tree in data[:4]:
        print(" ".join(words))
        print("   tags:", " ".join(tags))
    print("   tree of the first:", show_tree(data[0][2]))
    tokens = [w for words, _, _ in data for w in words]
    counts = Counter(tokens)
    print(f"\n{len(data)} sentences, {len(tokens)} tokens, {len(counts)} word types,"
          f" mean length {len(tokens) / len(data):.2f}")
    print("rank  word         count   rank x count")
    for r, (w, c) in enumerate(counts.most_common(), 1):
        if r in (1, 2, 3, 5, 10, 20, 30, 40):
            print(f"{r:4d}  {w:11s}  {c:6d}   {r * c:8d}")
    amb = Counter()
    for words, tags, _ in data:
        for w, t in zip(words, tags):
            amb[(w, t)] += 1
    for w in ("drills", "tracks", "samples"):
        print(f"'{w}': as a noun {amb[(w, 'N')]} times, as a verb {amb[(w, 'V')]} times")
