# Chapter 16: part-of-speech tagging with a hidden Markov model, and parsing with the CKY algorithm,
# both from scratch, on the toy corpus of ch16_grammar.py (whose true tags and trees we know).
import math
from collections import Counter, defaultdict
from ch16_grammar import RULES, corpus, show_tree

train, test = corpus(5000, 16), corpus(1000, 1601)

# ---------- Part 1: HMM tagging. States are tags, observations are words. ----------
class HMMTagger:
    def __init__(self, sents):
        self.trans, self.emit, self.tag_count, self.from_count = Counter(), Counter(), Counter(), Counter()
        for words, tags, _ in sents:
            prev = "<s>"
            for w, t in zip(words, tags):
                self.trans[(prev, t)] += 1
                self.emit[(t, w)] += 1
                self.tag_count[t] += 1
                prev = t
            self.trans[(prev, "</s>")] += 1
        for (a, _), c in self.trans.items():
            self.from_count[a] += c
        self.tags = sorted(self.tag_count)
        self.vocab = {w for words, _, _ in sents for w in words}

    def lp_trans(self, a, b):             # add-0.1 smoothing, in log space
        return math.log((self.trans[(a, b)] + 0.1) / (self.from_count[a] + 0.1 * (len(self.tags) + 1)))

    def lp_emit(self, t, w):              # an unseen word gets the same small share from every tag
        return math.log((self.emit[(t, w)] + 0.1) / (self.tag_count[t] + 0.1 * (len(self.vocab) + 1)))

    def tag(self, words):
        T = self.tags
        m = {t: self.lp_trans("<s>", t) + self.lp_emit(t, words[0]) for t in T}
        back = []
        for w in words[1:]:
            new, bp = {}, {}
            for t in T:
                best = max(T, key=lambda s: m[s] + self.lp_trans(s, t))
                new[t], bp[t] = m[best] + self.lp_trans(best, t) + self.lp_emit(t, w), best
            m = new
            back.append(bp)
        path = [max(T, key=lambda t: m[t] + self.lp_trans(t, "</s>"))]
        for bp in reversed(back):
            path.append(bp[path[-1]])
        return path[::-1]

    def baseline(self, w):                # the most frequent tag of the word (N if never seen)
        return max(self.tags, key=lambda t: self.emit[(t, w)]) if w in self.vocab else "N"


print("Part 1. HMM tagger, tested on 1000 held-out sentences")
print("  training sentences   HMM accuracy   most-frequent-tag   on drills/tracks/samples: HMM   baseline")
for size in (5, 50, 5000):
    h = HMMTagger(train[:size])
    right = base = total = amb = amb_right = amb_base = 0
    for words, tags, _ in test:
        guess = h.tag(words)
        for w, t, g in zip(words, tags, guess):
            total += 1
            right += g == t
            base += h.baseline(w) == t
            if w in ("drills", "tracks", "samples"):
                amb += 1
                amb_right += g == t
                amb_base += h.baseline(w) == t
    print(f"  {size:18d}   {right / total:12.4f}   {base / total:17.4f}   {amb_right / amb:29.4f}   {amb_base / amb:8.4f}")
h = HMMTagger(train)
for s in ("the rover drills the rock", "the drills tracks the dune", "the samples near the tracks waits"):
    print(f"  {s:38s} -> {' '.join(h.tag(s.split()))}")

# ---------- Part 2: CKY with the true grammar. ----------
binary, lexical = defaultdict(list), defaultdict(list)
for lhs, options in RULES.items():
    for rhs, p in options:
        if isinstance(rhs, str):
            lexical[rhs].append((lhs, p))
        else:
            binary[rhs].append((lhs, p))


def cky(words):
    """best[i][j][A] = (probability of the best tree for words i..j-1 rooted at A, back-pointer);
    inside[i][j][A] = total probability of all such trees."""
    n = len(words)
    best = [[{} for _ in range(n + 1)] for _ in range(n + 1)]
    inside = [[defaultdict(float) for _ in range(n + 1)] for _ in range(n + 1)]
    for i, w in enumerate(words):
        for A, p in lexical[w]:
            best[i][i + 1][A] = (p, w)
            inside[i][i + 1][A] += p
    for span in range(2, n + 1):
        for i in range(n - span + 1):
            j = i + span
            for k in range(i + 1, j):
                for B, (pb, _) in best[i][k].items():
                    for C, (pc, _) in best[k][j].items():
                        for A, p in binary.get((B, C), []):
                            q = p * pb * pc
                            if q > best[i][j].get(A, (0, None))[0]:
                                best[i][j][A] = (q, (k, B, C))
                            inside[i][j][A] += p * inside[i][k][B] * inside[k][j][C]
    return best, inside


def tree(best, i, j, A):
    p, bp = best[i][j][A]
    if isinstance(bp, str):
        return (A, bp)
    k, B, C = bp
    return (A, tree(best, i, k, B), tree(best, k, j, C))


print("\nPart 2. CKY parsing with the grammar's own probabilities")
for s in ("the rover sees the rock with the camera", "the rover sees the rock near the crater"):
    words = s.split()
    best, inside = cky(words)
    n = len(words)
    p_best = best[0][n]["S"][0]
    print(f"  {s}")
    print(f"    P(sentence) = {inside[0][n]['S']:.3e}, best parse {p_best:.3e}"
          f" ({p_best / inside[0][n]['S']:.3f} of the total)")
    print("    best:", show_tree(tree(best, 0, n, "S")))

# the number of parses grows fast with the number of prepositional phrases
def count_parses(words):
    n = len(words)
    cnt = [[defaultdict(int) for _ in range(n + 1)] for _ in range(n + 1)]
    for i, w in enumerate(words):
        for A, _ in lexical[w]:
            cnt[i][i + 1][A] += 1
    for span in range(2, n + 1):
        for i in range(n - span + 1):
            for k in range(i + 1, i + span):
                for B, cb in list(cnt[i][k].items()):
                    for C, cc in list(cnt[k][i + span].items()):
                        for A, _ in binary.get((B, C), []):
                            cnt[i][i + span][A] += cb * cc
    return cnt[0][n]["S"]


s = "the rover sees the rock"
print("  number of parses with k prepositional phrases appended:", end="")
for k in range(0, 7):
    print(f" {count_parses((s + ' near the dune' * k).split())}", end="")
print()

# the true per-word perplexity of the test set under the grammar (inside probabilities)
log_sum = n_tok = 0
for words, _, _ in test:
    _, inside = cky(words)
    log_sum += math.log2(inside[0][len(words)]["S"])
    n_tok += len(words) + 1                    # + 1 for the end of the sentence, as in the n-gram models
print(f"  perplexity of the 1000 test sentences under the true grammar: {2 ** (-log_sum / n_tok):.3f}")
