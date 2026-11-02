class HashMap:
    """A hash table with separate chaining: each bucket holds a short list of (key, value) pairs."""
    def __init__(self):
        self.buckets = [[] for _ in range(8)]
        self.size = 0

    def _bucket(self, key):
        return self.buckets[hash_str(key) % len(self.buckets)]

    def put(self, key, value):
        b = self._bucket(key)
        for i, (k, _) in enumerate(b):
            if k == key:
                b[i] = (key, value)          # key already there: replace its value
                return
        b.append((key, value))
        self.size += 1
        if self.size > 0.75 * len(self.buckets):   # too full: double the buckets
            self._resize(2 * len(self.buckets))

    def get(self, key, default=None):
        for k, v in self._bucket(key):
            if k == key:
                return v
        return default

    def _resize(self, n):
        old = self.buckets
        self.buckets = [[] for _ in range(n)]
        for b in old:
            for k, v in b:
                self.buckets[hash_str(k) % n].append((k, v))


def hash_str(s):
    """Polynomial string hash, the same as Java's String.hashCode, kept to 32 bits."""
    h = 0
    for ch in s:
        h = (31 * h + ord(ch)) & 0xFFFFFFFF
    return h


if __name__ == "__main__":
    text = "the quick brown fox jumps over the lazy dog the end"
    m = HashMap()
    for w in text.split():
        m.put(w, m.get(w, 0) + 1)
    for w in sorted(set(text.split())):
        print(w, m.get(w))
    print("buckets:", len(m.buckets), "keys:", m.size, "missing:", m.get("cat", 0))
    print(hash_str("abc"))
