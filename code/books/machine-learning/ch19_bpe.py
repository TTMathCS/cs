"""Chapter 19: byte-pair encoding (Sennrich, Haddow and Birch 2016) from scratch:
learn merges from word counts, then tokenize new words with them."""
import re
from collections import Counter


def learn_bpe(word_counts, num_merges, verbose=True):
    """word_counts: dict word -> count. Words are split into characters plus an
    end-of-word marker '_', then the most frequent adjacent pair is merged, again
    and again."""
    vocab = {tuple(w) + ("_",): c for w, c in word_counts.items()}
    merges = []
    for step in range(1, num_merges + 1):
        pairs = Counter()
        for symbols, c in vocab.items():
            for a, b in zip(symbols, symbols[1:]):
                pairs[a, b] += c
        if not pairs:
            break
        best = max(pairs, key=pairs.get)          # most frequent pair; ties: the first one seen
        merges.append(best)
        new_vocab = {}
        for symbols, c in vocab.items():
            out, i = [], 0
            while i < len(symbols):
                if i + 1 < len(symbols) and (symbols[i], symbols[i + 1]) == best:
                    out.append(symbols[i] + symbols[i + 1]); i += 2
                else:
                    out.append(symbols[i]); i += 1
            new_vocab[tuple(out)] = c
        vocab = new_vocab
        if verbose:
            shown = "  ".join(" ".join(s) + f" x{c}" for s, c in vocab.items())
            print(f"   merge {step:2d}: {best[0]} + {best[1]} (count {pairs[best]:2d})  ->  {shown}")
    return merges


def tokenize(word, merges):
    """Apply the learned merges in the order they were learned."""
    symbols = list(word) + ["_"]
    for a, b in merges:
        i, out = 0, []
        while i < len(symbols):
            if i + 1 < len(symbols) and symbols[i] == a and symbols[i + 1] == b:
                out.append(a + b); i += 2
            else:
                out.append(symbols[i]); i += 1
        symbols = out
    return symbols


print("1. Sennrich et al.'s example: low x5, lower x2, newest x6, widest x3")
toy = {"low": 5, "lower": 2, "newest": 6, "widest": 3}
merges = learn_bpe(toy, 10)
print()
print("2. tokenizing words never seen in training:")
for w in ("lowest", "newer", "wider", "slow"):
    print(f"   {w:7s} -> {tokenize(w, merges)}")

text = ("the rover drove to the rock and the rover drove back . the rovers drove to the rocks . "
        "a rover is driving ; rovers are driving ; the driver drove the rover . "
        "rocky ground slowed the rovers ; the rocky slope slowed the driver .")
counts = Counter(text.split())
merges2 = learn_bpe(counts, 25, verbose=False)
print()
print(f"3. a slightly bigger text: {sum(counts.values())} words, {len(counts)} distinct; 25 merges learned")
print("   first ten merges:", ", ".join(a + "+" + b for a, b in merges2[:10]))
for w in ("rovers", "driving", "rocky", "drivers", "unrocky"):
    print(f"   {w:8s} -> {tokenize(w, merges2)}")
chars_tokens = sum(len(w) + 1 for w in text.split())
bpe_tokens = sum(len(tokenize(w, merges2)) for w in text.split())
print(f"   tokens for the whole text: {chars_tokens} as characters, {bpe_tokens} after BPE")
