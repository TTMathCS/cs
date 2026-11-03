"""Chapter 2: turning categories and words into numbers.

One-hot and ordinal encoding of the flats' district and condition columns,
then the hashing trick for words, with a fixed hash so the results repeat.
"""
import hashlib
import numpy as np

DISTRICT = ["north", "south", "north", "east", "south", "east"]
CONDITION = ["good", "fair", "poor", "good", "good", "fair"]


def one_hot(values):
    """Return (categories, matrix) with one column per category."""
    cats = sorted(set(values))
    index = {c: j for j, c in enumerate(cats)}
    M = np.zeros((len(values), len(cats)), dtype=int)
    for i, v in enumerate(values):
        M[i, index[v]] = 1
    return cats, M


def one_hot_known(values, cats):
    """Encode with categories fixed in advance; unknown values become all zeros."""
    index = {c: j for j, c in enumerate(cats)}
    M = np.zeros((len(values), len(cats)), dtype=int)
    for i, v in enumerate(values):
        if v in index:
            M[i, index[v]] = 1
    return M


ORDER = {"poor": 0, "fair": 1, "good": 2}          # the order is real knowledge


def stable_hash(token):
    """A 32-bit hash that is the same on every run (Python's hash() is not)."""
    digest = hashlib.blake2b(token.encode("utf-8"), digest_size=4).digest()
    return int.from_bytes(digest, "big")


def hash_features(text, n_buckets=8, signed=True):
    """The hashing trick: word -> bucket by a hash, no vocabulary stored."""
    v = np.zeros(n_buckets, dtype=int)
    for word in text.lower().split():
        h = stable_hash(word)
        sign = 1 if (not signed or (h >> 31) & 1 == 0) else -1
        v[h % n_buckets] += sign
    return v


if __name__ == "__main__":
    cats, M = one_hot(DISTRICT)
    print("one-hot columns:", cats)
    for d, row in zip(DISTRICT, M):
        print(f"  {d:6} -> {row}")
    print("unseen district 'west' ->", one_hot_known(["west"], cats)[0])
    print("ordinal condition:", [ORDER[c] for c in CONDITION])

    print("\nhashing trick, 8 buckets")
    for w in ["dust", "storm", "near", "the", "crater", "rover", "panel", "covered", "in"]:
        h = stable_hash(w)
        print(f"  {w:7} hash = {h:10d}  bucket {h % 8}  sign {'+' if (h >> 31) & 1 == 0 else '-'}")
    for text in ["dust storm near the crater", "rover panel covered in dust"]:
        print(f"  {text!r:31} -> {hash_features(text)}")

    # How often do two different words share a bucket?  For m words in b buckets
    # the expected number of colliding pairs is C(m, 2) / b.
    words = ["w%d" % i for i in range(1000)]
    for b in (1024, 2 ** 16):
        buckets = [stable_hash(w) % b for w in words]
        counts = np.bincount(buckets, minlength=b)
        pairs = int((counts * (counts - 1) // 2).sum())
        print(f"1000 words into {b:5d} buckets: {pairs} colliding pairs"
              f" (expected {1000 * 999 / 2 / b:.1f})")
