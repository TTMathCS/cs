"""Chapter 12.2: multinomial naive Bayes for spam from scratch, with Laplace smoothing,
computed in log space. The corpus is a tiny made-up table typed into the file."""
from collections import Counter
from math import log, exp

TRAIN = [
    ("spam", "win money now"), ("spam", "free money offer"), ("spam", "win a free prize now"),
    ("spam", "cheap offer win cash"), ("spam", "free cash prize claim now"),
    ("spam", "claim your free offer"),
    ("ham", "meeting moved to monday"), ("ham", "lunch on monday"), ("ham", "project meeting notes attached"),
    ("ham", "can we move lunch"), ("ham", "notes from the project review"), ("ham", "see you at the meeting"),
    ("ham", "your review is attached"), ("ham", "monday lunch at noon"),
]
TEST = [("spam", "free money"), ("ham", "project lunch monday"), ("spam", "claim cash now"),
        ("ham", "meeting notes"), ("spam", "win a cheap prize"), ("ham", "review the offer on monday")]


def train(data, alpha):
    classes = sorted({c for c, _ in data})
    prior = {c: sum(1 for k, _ in data if k == c) / len(data) for c in classes}
    counts = {c: Counter(w for k, m in data if k == c for w in m.split()) for c in classes}
    vocab = sorted(set().union(*counts.values()))
    total = {c: sum(counts[c].values()) for c in classes}
    V = len(vocab)

    def p_word(w, c):   # (count + alpha) / (total + alpha V): the smoothed estimate
        return (counts[c][w] + alpha) / (total[c] + alpha * V)
    return classes, prior, p_word, vocab, counts, total


def log_scores(msg, model):
    classes, prior, p_word, vocab, _, _ = model
    out = {}
    for c in classes:
        s = log(prior[c])
        for w in msg.split():
            if w not in vocab:
                continue                   # a word never seen in training carries no evidence
            p = p_word(w, c)
            s += log(p) if p > 0 else float("-inf")
        out[c] = s
    return out


def posterior(scores):
    m = max(scores.values())
    if m == float("-inf"):
        return {c: float("nan") for c in scores}
    z = sum(exp(s - m) for s in scores.values())   # subtract the max: the log-sum-exp trick
    return {c: exp(s - m) / z for c, s in scores.items()}


model = train(TRAIN, alpha=1.0)
classes, prior, p_word, vocab, counts, total = model
print(f"vocabulary: {len(vocab)} words; words in spam: {total['spam']}, in ham: {total['ham']}")
print(f"priors: P(spam) = {prior['spam']:.4f}, P(ham) = {prior['ham']:.4f}")
print("\nSmoothed word probabilities (alpha = 1)")
print("  word      count spam  P(w|spam)  count ham  P(w|ham)")
for w in ["free", "money", "now", "monday", "meeting", "offer", "review"]:
    print(f"  {w:8s}  {counts['spam'][w]:10d}  {p_word(w, 'spam'):9.4f}  {counts['ham'][w]:9d}  {p_word(w, 'ham'):8.4f}")

print("\nHand example: the message 'free money'")
s = log_scores("free money", model)
for c in classes:
    print(f"  log P({c}) + log P(free|{c}) + log P(money|{c}) = {s[c]:.4f}")
post = posterior(s)
print(f"  P(spam | 'free money') = {post['spam']:.4f}")

print("\nTest messages")
for alpha in [1.0, 0.0]:
    m = train(TRAIN, alpha)
    print(f"  alpha = {alpha}:")
    for label, msg in TEST:
        p = posterior(log_scores(msg, m))
        print(f"    {msg:28s} true {label:4s}  P(spam) = {p['spam']:.4f}")
print("With alpha = 0 one unseen (word, class) pair forces a probability of exactly 0 or 1,")
print("and a message with one word never seen in spam and another never seen in ham")
print("gets 0/0: no answer at all (nan).")
