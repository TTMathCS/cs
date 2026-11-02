class TrieNode:
    def __init__(self):
        self.children = {}                   # letter -> next node
        self.end = False                     # does a word end here?
        self.count = 0                       # how many words pass through here


class Trie:
    """A prefix tree of words: insert, look up and count by prefix in O(length of the word)."""
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
            node.count += 1
        node.end = True

    def _walk(self, s):
        node = self.root
        for ch in s:
            node = node.children.get(ch)
            if node is None:
                return None
        return node

    def contains(self, word):
        node = self._walk(word)
        return node is not None and node.end

    def count_prefix(self, prefix):
        node = self._walk(prefix)
        return 0 if node is None else node.count

    def with_prefix(self, prefix):
        """All stored words that start with prefix, in alphabetical order."""
        out = []

        def dfs(node, path):
            if node.end:
                out.append(path)
            for ch in sorted(node.children):
                dfs(node.children[ch], path + ch)
        node = self._walk(prefix)
        if node is not None:
            dfs(node, prefix)
        return out


if __name__ == "__main__":
    t = Trie()
    for w in ["mars", "marble", "march", "mare", "moon", "moonlight", "map"]:
        t.insert(w)
    print(t.contains("mars"), t.contains("mar"), t.contains("moonlit"))
    print(t.count_prefix("mar"), t.count_prefix("moon"), t.count_prefix("x"))
    print(t.with_prefix("mar"))
    print(t.with_prefix("mo"))
