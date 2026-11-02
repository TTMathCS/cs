import heapq


def huffman(freq):
    """Huffman coding: the prefix-free binary code with the fewest total bits for these letter counts.
    freq is a list of (letter, count). Returns {letter: code}. Ties are broken by creation order, so the
    result is the same in every language."""
    heap = []                                # entries (count, id); ids 0..n-1 are the letters
    left, right = {}, {}
    for i, (_, f) in enumerate(freq):
        heapq.heappush(heap, (f, i))
    next_id = len(freq)
    while len(heap) > 1:                     # join the two rarest trees into one
        f1, a = heapq.heappop(heap)
        f2, b = heapq.heappop(heap)
        left[next_id], right[next_id] = a, b
        heapq.heappush(heap, (f1 + f2, next_id))
        next_id += 1
    codes = {}

    def walk(node, path):                    # left edge = 0, right edge = 1
        if node < len(freq):
            codes[freq[node][0]] = path or "0"
        else:
            walk(left[node], path + "0")
            walk(right[node], path + "1")
    walk(heap[0][1], "")
    return codes


if __name__ == "__main__":
    freq = [("a", 45), ("b", 13), ("c", 12), ("d", 16), ("e", 9), ("f", 5)]
    codes = huffman(freq)
    for letter, _ in freq:
        print(letter, codes[letter])
    total = sum(f * len(codes[ch]) for ch, f in freq)
    print("total bits:", total, "fixed 3-bit code:", 3 * sum(f for _, f in freq))
    print("face ->", "".join(codes[ch] for ch in "face"))
