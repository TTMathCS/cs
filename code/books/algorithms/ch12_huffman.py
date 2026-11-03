"""Chapter 12: Huffman coding from scratch, checked against every prefix code tree."""
import heapq
import math
from collections import Counter
from itertools import count


def huffman_code(freq):
    """freq: dict symbol -> weight. Returns dict symbol -> bit string."""
    tick = count()                       # breaks ties so heapq never compares trees
    heap = [(w, next(tick), sym) for sym, w in freq.items()]
    heapq.heapify(heap)
    if len(heap) == 1:
        return {heap[0][2]: "0"}, []
    merges = []
    while len(heap) > 1:
        w1, _, t1 = heapq.heappop(heap)  # the two lightest trees
        w2, _, t2 = heapq.heappop(heap)
        merges.append((w1, w2))
        heapq.heappush(heap, (w1 + w2, next(tick), (t1, t2)))
    code = {}

    def walk(tree, prefix):
        if isinstance(tree, tuple):
            walk(tree[0], prefix + "0")
            walk(tree[1], prefix + "1")
        else:
            code[tree] = prefix
    walk(heap[0][2], "")
    return code, merges


def cost(code, freq):
    return sum(freq[s] * len(code[s]) for s in freq)


def decode(bits, code):
    back = {v: k for k, v in code.items()}
    out, cur = [], ""
    for b in bits:
        cur += b
        if cur in back:                  # prefix-free: the first match is the symbol
            out.append(back[cur])
            cur = ""
    return "".join(out)


def best_full_tree_cost(weights):
    """Exhaustive optimum over all ways of building a full binary tree (small inputs)."""
    weights = tuple(sorted(weights))
    memo = {}

    def best(ws):
        if len(ws) == 1:
            return 0
        if ws in memo:
            return memo[ws]
        result = math.inf
        for i in range(len(ws)):
            for j in range(i + 1, len(ws)):  # merge ANY two, not just the lightest
                rest = ws[:i] + ws[i + 1:j] + ws[j + 1:]
                merged = tuple(sorted(rest + (ws[i] + ws[j],)))
                result = min(result, ws[i] + ws[j] + best(merged))
        memo[ws] = result
        return result
    return best(weights)


if __name__ == "__main__":
    freq = {"a": 45, "b": 13, "c": 12, "d": 16, "e": 9, "f": 5}
    code, merges = huffman_code(freq)
    print("merges (lighter, heavier):", merges)
    for s in sorted(code):
        print(f"  {s}: weight {freq[s]:2d}  code {code[s]}")
    print("total bits for 100 symbols:", cost(code, freq), " (fixed 3-bit code: 300)")

    text = "abracadabra alakazam"
    f = Counter(text)
    c, _ = huffman_code(f)
    bits = "".join(c[ch] for ch in text)
    n = len(text)
    entropy = -sum(w / n * math.log2(w / n) for w in f.values())
    print(f"\n'{text}': {len(bits)} bits, {len(bits) / n:.3f} bits per symbol, "
          f"entropy {entropy:.3f}")
    print("decodes back correctly:", decode(bits, c) == text)
    print("Huffman cost equals exhaustive optimum on the 6-symbol example:",
          cost(code, freq) == best_full_tree_cost(freq.values()))
