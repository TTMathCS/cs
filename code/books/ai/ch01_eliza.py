"""Chapter 1: a tiny ELIZA, built from scratch.

Weizenbaum's ELIZA (1966) had no model of the world at all. It looked for a
keyword in what you typed, cut the sentence into pieces with a pattern, swapped
pronouns ("my" -> "your"), and pasted the pieces into a canned reply. This
version follows the same plan with a small DOCTOR-like script: keywords with
ranks, decomposition patterns with wildcards, reassembly templates used in
turn, and pronoun reflection. Standard library only.
"""
import re

# Pronoun reflection: applied to the pieces that are copied back.
REFLECT = {"i": "you", "me": "you", "my": "your", "am": "are", "mine": "yours",
           "myself": "yourself", "you": "I", "your": "my", "yours": "mine",
           "are": "am", "i'm": "you are", "was": "were"}

# Script: keyword -> (rank, [(decomposition pattern, [reassembly templates])]).
# In a pattern, "*" matches any run of words (possibly empty). {1}, {2}, ...
# in a template are replaced by the reflected text matched by the stars.
SCRIPT = {
    "mother": (3, [("* my mother *", ["Tell me more about your family.",
                                       "Who else in your family {2}?"])]),
    "father": (3, [("* my father *", ["Your father {2}?",
                                       "Does he influence you strongly?"])]),
    "i": (1, [("* i am *", ["How long have you been {2}?",
                            "Do you believe it is normal to be {2}?"]),
              ("* i want *", ["What would it mean to you if you got {2}?",
                              "Why do you want {2}?"]),
              ("* i feel *", ["Do you often feel {2}?",
                              "Tell me more about such feelings."]),
              ("*", ["You say {1}?", "Can you elaborate on that?"])]),
    "because": (2, [("*", ["Is that the real reason?",
                           "What other reasons come to mind?"])]),
    "computer": (4, [("*", ["Do computers worry you?",
                            "Why do you mention computers?"])]),
    "always": (2, [("*", ["Can you think of a specific example?"])]),
}
NO_KEYWORD = ["Please go on.", "I see.", "What does that suggest to you?"]


def words(text):
    return re.findall(r"[a-z']+", text.lower())


def reflect(ws):
    return " ".join(REFLECT.get(w, w) for w in ws)


def match(pattern, ws):
    """Match a pattern like '* i am *' against a word list.
    Returns the list of word lists matched by the stars, or None."""
    pat = pattern.split()

    def go(i, j):
        if i == len(pat):
            return [] if j == len(ws) else None
        if pat[i] == "*":
            for k in range(j, len(ws) + 1):   # try shortest first
                rest = go(i + 1, k)
                if rest is not None:
                    return [ws[j:k]] + rest
            return None
        if j < len(ws) and ws[j] == pat[i]:
            return go(i + 1, j + 1)
        return None

    return go(0, 0)


class Eliza:
    def __init__(self):
        self.turn = {}          # (keyword, pattern) -> next template index
        self.default = 0

    def reply(self, text):
        ws = words(text)
        keys = sorted((k for k in set(ws) if k in SCRIPT),
                      key=lambda k: -SCRIPT[k][0])
        for k in keys:                        # highest-ranked keyword first
            for pattern, templates in SCRIPT[k][1]:
                parts = match(pattern, ws)
                if parts is None:
                    continue
                n = self.turn.get((k, pattern), 0)
                self.turn[(k, pattern)] = n + 1
                t = templates[n % len(templates)]
                for idx, p in enumerate(parts, start=1):
                    t = t.replace("{%d}" % idx, reflect(p))
                return t, k
        t = NO_KEYWORD[self.default % len(NO_KEYWORD)]
        self.default += 1
        return t, None


def main():
    print("pattern match '* i am *' on 'well i am very unhappy today':")
    print("  stars ->", match("* i am *", words("well i am very unhappy today")))
    print("reflect 'my plans and me' ->", reflect(words("my plans and me")))
    print()
    eliza = Eliza()
    talk = ["Men are all alike.",
            "They're always bugging us about something.",
            "Well, my father made me come here.",
            "I am unhappy about my work.",
            "I want a quieter office.",
            "Because the computer room is noisy.",
            "I feel nobody listens to me.",
            "The weather on Mars is cold.",
            "I am unhappy about my work."]
    for line in talk:
        r, k = eliza.reply(line)
        print(f"> {line}")
        print(f"  {r}   [keyword: {k}]")


if __name__ == "__main__":
    main()
