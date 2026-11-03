# Chapter 17: retrieval-augmented generation and a ReAct-style tool loop, from scratch.
# The "language model" is a FAKE: a few lines of rules standing in for a real network, so that every
# step of the loop around it (retrieve, prompt, parse the action, run the tool, append the observation)
# is visible. A real system swaps the fake for a real model and keeps the loop.
import math
import re
from collections import Counter

DOCS = [
    "Dijkstra published his shortest path algorithm in 1959.",
    "Hart, Nilsson and Raphael published the A* search algorithm in 1968.",
    "Kalman published the Kalman filter in 1960.",
    "Robinson published the unification algorithm for resolution in 1965.",
    "Light takes between about 3 and 22 minutes to travel one way between Mars and Earth.",
    "Deep Blue defeated the world chess champion Garry Kasparov in a match in 1997.",
]
STOP = {"the", "a", "an", "in", "of", "for", "and", "to", "his", "between", "about", "what", "when",
        "who", "did", "was", "is", "how", "many", "years", "after", "published", "year"}


def words(text):
    return [w for w in re.findall(r"[a-z0-9*]+", text.lower()) if w not in STOP]


# ---- retrieval: TF-IDF vectors and cosine similarity ----------------------------------------
N = len(DOCS)
df = Counter(w for d in DOCS for w in set(words(d)))
idf = {w: math.log(N / df[w]) + 1 for w in df}


def tfidf(text):
    tf = Counter(w for w in words(text) if w in idf)
    return {w: c * idf[w] for w, c in tf.items()}


def cosine(u, v):
    dot = sum(u[w] * v.get(w, 0) for w in u)
    nu, nv = math.sqrt(sum(x * x for x in u.values())), math.sqrt(sum(x * x for x in v.values()))
    return dot / (nu * nv) if nu and nv else 0.0


DOC_VECS = [tfidf(d) for d in DOCS]


def retrieve(query, k=2):
    qv = tfidf(query)
    scores = sorted(((cosine(qv, dv), i) for i, dv in enumerate(DOC_VECS)), reverse=True)
    return [(round(s, 3), DOCS[i]) for s, i in scores[:k]]


# ---- the fake model ---------------------------------------------------------------------------
def fake_model_answer(prompt):
    """Answers from the context if a context sentence shares a keyword with the question and holds a
    year; with no usable context it does what a bare language model may do: produce a fluent guess."""
    q = prompt.split("Question:")[1]
    ctx = prompt.split("Question:")[0]
    best = max(ctx.split("\n"), key=lambda s: len(set(words(s)) & set(words(q))))
    year = re.search(r"\b(1[89]\d\d|20\d\d)\b", best)
    if year and set(words(best)) & set(words(q)):
        return f"{year.group(1)} (from: {best.strip()[:45]}...)"
    return "1957 (no source)"           # fluent, confident and unsupported: a hallucination


print("1. retrieval-augmented generation")
question = "In what year was the A* search algorithm published?"
hits = retrieve(question)
for s, d in hits:
    print(f"   retrieved (cosine {s}): {d}")
prompt = "Context:\n" + "\n".join(d for _, d in hits) + "\nQuestion: " + question
print("   with retrieval   :", fake_model_answer(prompt))
print("   without retrieval:", fake_model_answer("Context:\n\nQuestion: " + question))


# ---- tools and the ReAct loop -------------------------------------------------------------------
def calculator(expr):
    if not re.fullmatch(r"[0-9+\-*/ ().]+", expr):  # only arithmetic, never arbitrary code
        return "error: not an arithmetic expression"
    return str(eval(expr, {"__builtins__": {}}))


TOOLS = {"search": lambda arg: retrieve(arg, k=1)[0][1], "calculate": calculator}


def fake_model_react(transcript):
    """Writes the next 'Thought: ... Action: tool[argument]' or 'Final Answer: ...' line,
    looking only at the transcript, as a real model would."""
    obs = re.findall(r"Observation: (.*)", transcript)
    years = [re.search(r"\b(1[89]\d\d)\b", o).group(1) for o in obs if re.search(r"\b(1[89]\d\d)\b", o)]
    if len(years) == 0:
        return "Thought: I need the year of Dijkstra's algorithm.\nAction: search[Dijkstra shortest path algorithm]"
    if len(years) == 1:
        return "Thought: Now I need the year of A*.\nAction: search[A* search algorithm]"
    if not any(re.fullmatch(r"-?\d+", o) for o in obs):
        return f"Thought: Subtract the years.\nAction: calculate[{years[1]} - {years[0]}]"
    return f"Thought: I have the difference.\nFinal Answer: {obs[-1]} years"


def react(question, max_steps=6):
    transcript = f"Question: {question}\n"
    for step in range(max_steps):           # a step limit: the loop must end even if the model never does
        out = fake_model_react(transcript)
        transcript += out + "\n"
        if "Final Answer:" in out:
            return transcript
        m = re.search(r"Action: (\w+)\[(.*)\]", out)
        if not m or m.group(1) not in TOOLS:
            transcript += "Observation: error: unknown action\n"
            continue
        transcript += f"Observation: {TOOLS[m.group(1)](m.group(2))}\n"
    return transcript + "Stopped: step limit reached\n"


print("\n2. a ReAct loop with two tools (search, calculate)")
for line in react("How many years after Dijkstra's algorithm was A* published?").strip().split("\n"):
    print("   " + line)
print("\n3. the calculator refuses non-arithmetic:", calculator("__import__('os')"))
