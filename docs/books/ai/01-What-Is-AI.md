# 1. What is artificial intelligence?

*People argue about what "artificial intelligence" means, and the argument is not just about words: what you count
as intelligence decides what you try to build and how you test it. This chapter sorts the main definitions into four
families, reads Alan Turing's 1950 proposal for testing a machine and finds where it falls short, and walks through
an honest history of the field, from the 1955 Dartmouth proposal through expert systems, two "winters", statistical
methods, deep learning and language models. You will build two historic kinds of program from scratch, a tiny ELIZA
and a tiny rule-based expert system, and see both what they do and why they are not what they seem. The chapter ends
with what today's systems can and cannot do, and the map of the rest of this book.*

!!! abstract "In this chapter"
    **You will learn:**

    - the four families of definitions of AI (thinking or acting, like a human or rationally) and why this book
      takes the rational-agent view
    - Turing's imitation game, what it tests, and its limits (ELIZA, the Chinese room, the Winograd schemas)
    - how ELIZA worked, by building one: keywords, patterns, pronoun reflection
    - how a rule-based expert system works, by building one with MYCIN-style certainty factors, and why such
      systems were brittle
    - an honest history of AI: Dartmouth, the early programs, expert systems, the winters, statistical AI, deep
      learning and language models
    - the difference between narrow and general AI, and a sober list of what current systems do and do not do

    **You need:** nothing beyond curiosity and the habit of reading a short Python program.
    [Chapter 1 of the Algorithms book](../algorithms/01-What-Is-an-Algorithm.md) explains what an algorithm is and
    what a Turing machine is, if those words are new.

    **Levels:** 1.1 to 1.3 are beginner; 1.4 is beginner to intermediate; 1.5 is for everyone.

## 1.1 Four definitions

Is a pocket calculator intelligent? It multiplies 12-digit numbers faster and more reliably than any person. Most
people say no: it does one fixed thing, it never surprises us, and it does not "know" what a number is. Is a chess
program intelligent? It beats every human player. Many people hesitate here. Is a program that writes a fluent essay
intelligent? People disagree loudly. The word **intelligence** has no agreed definition even for people, so it is no
surprise that **artificial intelligence** (AI), the attempt to build intelligence in machines, has several.

Russell and Norvig, in the textbook most courses use, sort the definitions along two questions.

1. **Thinking or acting?** Do we care about the *processes* inside the machine (reasoning, believing, planning), or
   only about its *behaviour* (what it does in the world)?
2. **Humanly or rationally?** Do we measure success against *people* (does it think or act like a human?), or
   against an ideal standard of *rationality* (does it think or act correctly, given what it knows?)

Two questions with two answers each give four families.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 600 300" role="img" aria-label="A two by two grid. Columns: humanly, rationally. Rows: thinking, acting. Cells: thinking humanly, cognitive modelling; thinking rationally, laws of thought and logic; acting humanly, the Turing test; acting rationally, rational agents, the view of this book, highlighted.">
  <text x="245" y="30" font-size="14" font-weight="bold" text-anchor="middle" fill="currentColor">humanly</text>
  <text x="465" y="30" font-size="14" font-weight="bold" text-anchor="middle" fill="currentColor">rationally</text>
  <text x="70" y="110" font-size="14" font-weight="bold" text-anchor="middle" fill="currentColor">thinking</text>
  <text x="70" y="230" font-size="14" font-weight="bold" text-anchor="middle" fill="currentColor">acting</text>
  <rect x="140" y="45" width="210" height="120" rx="8" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor"/>
  <text x="245" y="85" font-size="14" text-anchor="middle" fill="currentColor">thinking humanly</text>
  <text x="245" y="110" font-size="12" text-anchor="middle" fill="currentColor">cognitive modelling:</text>
  <text x="245" y="128" font-size="12" text-anchor="middle" fill="currentColor">does it reason the way</text>
  <text x="245" y="146" font-size="12" text-anchor="middle" fill="currentColor">people reason?</text>
  <rect x="360" y="45" width="210" height="120" rx="8" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor"/>
  <text x="465" y="85" font-size="14" text-anchor="middle" fill="currentColor">thinking rationally</text>
  <text x="465" y="110" font-size="12" text-anchor="middle" fill="currentColor">laws of thought:</text>
  <text x="465" y="128" font-size="12" text-anchor="middle" fill="currentColor">does it draw only</text>
  <text x="465" y="146" font-size="12" text-anchor="middle" fill="currentColor">correct conclusions?</text>
  <rect x="140" y="170" width="210" height="120" rx="8" fill="#eea66f" fill-opacity="0.35" stroke="currentColor"/>
  <text x="245" y="210" font-size="14" text-anchor="middle" fill="currentColor">acting humanly</text>
  <text x="245" y="235" font-size="12" text-anchor="middle" fill="currentColor">the Turing test:</text>
  <text x="245" y="253" font-size="12" text-anchor="middle" fill="currentColor">can you tell it apart</text>
  <text x="245" y="271" font-size="12" text-anchor="middle" fill="currentColor">from a person?</text>
  <rect x="360" y="170" width="210" height="120" rx="8" fill="#7ccf9a" fill-opacity="0.45" stroke="currentColor" stroke-width="2.5"/>
  <text x="465" y="210" font-size="14" text-anchor="middle" fill="currentColor">acting rationally</text>
  <text x="465" y="235" font-size="12" text-anchor="middle" fill="currentColor">rational agents:</text>
  <text x="465" y="253" font-size="12" text-anchor="middle" fill="currentColor">does it do the best it can,</text>
  <text x="465" y="271" font-size="12" text-anchor="middle" fill="currentColor">given what it knows?</text>
</svg>
<figcaption>Figure 1.1. Four families of definitions of AI, after Russell and Norvig. The rows ask whether we judge
the inner process or the outward behaviour; the columns ask whether the yardstick is human performance or ideal
rationality. This book works in the bottom-right cell.</figcaption>
</figure>

### Thinking humanly: cognitive modelling

To say a program thinks like a human, we first need to know how humans think. There are three ways to find out:
look inward (introspection, which is unreliable), watch people solve problems (psychology experiments), and watch the
brain at work (brain imaging and neuroscience). **Cognitive science** brings these together with computer models.
Allen Newell and Herbert Simon, whose Logic Theorist and General Problem Solver appear in Section 1.3, cared not only
that their programs solved problems but that they solved them by steps resembling the "thinking aloud" records of
human subjects. A model in this family is good if it makes the same mistakes as people, takes longer on the problems
people find harder, and so on.

This is a scientific goal (understanding the human mind) more than an engineering one. It is valuable, but it is
not what this book is about: a route planner that searches millions of states, which no person could do, is useful
precisely because it does *not* think like us.

### Thinking rationally: the laws of thought

The Greek philosopher Aristotle tried to write down patterns of correct argument, his **syllogisms**: "all
astronauts are humans; all humans are mortal; therefore all astronauts are mortal." The conclusion follows from the
premises by form alone, whatever the words mean. Logicians of the 19th and 20th centuries (Boole, Frege and others)
made this precise as **formal logic**: a language for statements about objects and relations, with rules of
inference that never lead from true premises to a false conclusion. By about 1965 there were programs that could, in
principle, prove any provable statement written in first-order logic (Chapter 9).

The **logicist** idea is to build intelligence on this: write what you know in logic, and let a theorem prover
derive what to do. Two problems appear at once. First, much knowledge is not certain ("birds fly", "the road is
probably clear"), and logic has no place for "probably"; Part IV of this book, on probability, is the fix. Second,
there is a big gap between being able to prove something *in principle* and proving it *in practice*: a problem
with a few hundred facts can make a prover search for longer than the age of the universe. Chapters 3 to 8 are about
closing that gap.

### Acting humanly: the Turing test

Alan Turing proposed in 1950 to stop asking whether a machine thinks and ask instead whether its behaviour in a
conversation can be told apart from a person's. Section 1.2 looks at this proposal closely. To pass such a test, a
machine would need to understand language, store what it knows and is told, reason with it, and learn and adapt.
Those four abilities, **natural language processing**, **knowledge representation**, **automated reasoning** and
**machine learning**, are still major parts of AI. A stronger version, sometimes called the total Turing test,
adds seeing and moving things (perception and robotics).

### Acting rationally: the rational agent

An **agent** is anything that perceives its environment and acts on it: a person, a thermostat, a rover, a
program. A **rational agent** is one that acts so as to achieve the best expected outcome, given what it has
perceived and what it knows. "Best" is measured by a **performance measure** we choose: arrive safely, clean the
floor, win the game.

This is the view this book takes, for three reasons.

- It is **more general than thinking rationally.** Correct logical inference is one way to act well, but not the
  only one. Pulling your hand off a hot stove is rational and involves no deliberation. A rational agent may use
  logic, probability, search, learning or a reflex, whatever works best.
- It is **more precise than acting humanly.** "Like a person" is a moving, fuzzy target. "Maximises the expected
  value of this performance measure" is a mathematical statement that we can analyse, prove things about and
  build toward.
- It **separates the goal from the method.** We can ask what the best possible behaviour is (even when it cannot be
  computed), and then how close a given program gets.

One honest qualification. Perfect rationality is usually impossible: computing the best action exactly would take
too long in any interesting environment. So the real goal is **limited** (or bounded) rationality: act as well as
possible with the time and memory available. Much of this book is about that trade-off, for example search that
stops early with a good answer instead of a perfect one (Chapter 4, Section 4.5).

### A warning built into the definition

The rational-agent view has a weak point that is technical, not philosophical. The agent is only as good as the
performance measure we give it. If the measure says "points for each piece of dirt sucked up", a rational vacuum
cleaner might learn to dump dirt and suck it up again. Russell and Norvig, in their 2020 edition, call the habit of
building machines that optimise a fixed, given objective the "standard model" of AI, and point out that much of the
difficulty of building beneficial systems is in getting the objective right. Chapter 2 builds that vacuum and
measures the effect; Chapters 15 and 20 return to the problem as **specification gaming**.

### What other authors have said

Textbooks and pioneers have given many one-line definitions. A few, in paraphrase, show the spread:

| Author(s) | Definition, paraphrased | Family |
|---|---|---|
| McCarthy and colleagues, Dartmouth proposal (1955) | every feature of intelligence can be described so precisely that a machine can simulate it | thinking (process) |
| Kurzweil (1990) | making machines perform tasks that need intelligence when people do them | acting humanly |
| Rich and Knight (1991) | getting computers to do things at which, for now, people are better | acting humanly |
| Poole, Mackworth and Goebel (1998) | the study of the design of intelligent agents | acting rationally |
| Nilsson (1998) | intelligent behaviour in artefacts | acting rationally |

The Rich and Knight definition has an odd consequence: once computers do something well, it stops being AI. This
"moving goalpost" effect is real. Route planning, spelling correction and chess were all once AI research topics;
now most people just call them software.

## 1.2 Turing's question and the imitation game

In October 1950 the journal *Mind* published Alan Turing's paper "Computing Machinery and Intelligence". It begins:
"I propose to consider the question, 'Can machines think?'" Turing immediately says the question is too vague to
answer, because the words "machine" and "think" are used loosely, and he replaces it with a game.

### The game

The **imitation game** has three players: a machine (A), a human (B) and a human interrogator (C) in another room.
The interrogator talks to A and B only by typed messages, so that voice and appearance do not matter, and must decide
which is the machine. The machine tries to be mistaken for the human; the human tries to help the interrogator.
Turing's new question: are there imaginable machines that would do well in this game?

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 600 220" role="img" aria-label="The imitation game. An interrogator on the left sends typed questions through a wall to two hidden players, X and Y; one is a machine, one is a person. The interrogator must say which is which.">
  <rect x="20" y="70" width="140" height="80" rx="8" fill="#9cc9ea" fill-opacity="0.4" stroke="currentColor"/>
  <text x="90" y="105" font-size="14" text-anchor="middle" fill="currentColor">interrogator</text>
  <text x="90" y="127" font-size="12" text-anchor="middle" fill="currentColor">types questions</text>
  <line x1="290" y1="20" x2="290" y2="200" stroke="currentColor" stroke-width="3" stroke-dasharray="8 5"/>
  <text x="290" y="214" font-size="12" text-anchor="middle" fill="currentColor">wall: text only</text>
  <line x1="160" y1="95" x2="400" y2="58" stroke="currentColor" stroke-width="1.5"/>
  <line x1="160" y1="125" x2="400" y2="162" stroke="currentColor" stroke-width="1.5"/>
  <polygon points="408,57 398,52 399,63" fill="currentColor"/>
  <polygon points="408,163 399,157 398,168" fill="currentColor"/>
  <rect x="410" y="25" width="170" height="64" rx="8" fill="#eea66f" fill-opacity="0.35" stroke="currentColor"/>
  <text x="495" y="52" font-size="14" text-anchor="middle" fill="currentColor">player X</text>
  <text x="495" y="73" font-size="12" text-anchor="middle" fill="currentColor">machine or person?</text>
  <rect x="410" y="131" width="170" height="64" rx="8" fill="#7ccf9a" fill-opacity="0.4" stroke="currentColor"/>
  <text x="495" y="158" font-size="14" text-anchor="middle" fill="currentColor">player Y</text>
  <text x="495" y="179" font-size="12" text-anchor="middle" fill="currentColor">person or machine?</text>
  <text x="205" y="62" font-size="11" text-anchor="middle" fill="currentColor">"Q: write me a sonnet"</text>
  <text x="200" y="170" font-size="11" text-anchor="middle" fill="currentColor">"Q: add 34957 to 70764"</text>
</svg>
<figcaption>Figure 1.2. Turing's imitation game. The interrogator sees only text and must decide which hidden player
is the machine. The two sample questions are from Turing's own imagined dialogue.</figcaption>
</figure>

Turing's paper is still worth reading because it is careful. He made a prediction: that in about fifty years it
would be possible to program computers with a storage capacity of about $10^9$ to play the game so well that "an
average interrogator will not have more than 70 per cent. chance of making the right identification after five
minutes of questioning." Note how modest and specific this is: five minutes, an average interrogator, a 70 percent
success rate for the *interrogator*, not a machine that fools everyone forever.

He then answered nine objections he expected, among them:

- **The argument from consciousness.** A machine might act as if it feels, but we cannot know it feels. Turing's
  reply: we cannot know this of other people either; we grant them minds by the "polite convention" of judging
  behaviour.
- **The mathematical objection.** Gödel's incompleteness theorem shows that any consistent formal system has true
  statements it cannot prove, so a machine has limits. Turing's reply: so might people; nobody has shown humans are
  free of such limits.
- **Lady Lovelace's objection.** Ada Lovelace wrote in 1843 that Babbage's Analytical Engine "has no pretensions to
  originate anything. It can do whatever we know how to order it to perform." Turing's reply is the final section of his paper,
  **learning machines**: rather than programming an adult mind, build a "child machine" and educate it. That is a
  description of machine learning, in 1950.

The paper ends: "We can only see a short distance ahead, but we can see plenty there that needs to be done."

### What the test gets right

The test is **operational**: it replaces a question nobody can settle ("does it really think?") with an experiment
anyone can run. It is **broad**: conversation can range over any topic, so a machine cannot pass by being good at
one thing. And it is **fair** in one specific sense: it judges the machine by the same evidence we use for each
other.

### Its limits

The test has been criticised from several sides, and the criticisms are why AI research does not try to pass it.

**It can be gamed by tricks.** The first warning came from a program that was not even trying to pass. Joseph
Weizenbaum's ELIZA (1966) imitated a psychotherapist who answers mostly by turning the patient's words back into
questions. It had no model of anything; it matched keywords. Weizenbaum later wrote, in *Computer Power and Human
Reason* (1976), that he was startled by how readily people who knew it was a program confided in it. Fooling people
is easier than understanding them. We build an ELIZA below.

**It is anthropocentric.** It tests for *human-like* intelligence, including human weaknesses. A machine that
answered "add 34957 to 70764" instantly and correctly would be unmasked; to pass, it must pause and sometimes make
mistakes. (Turing knew this: in his sample dialogue the "machine" pauses about 30 seconds and gives a wrong sum.)
Aeronautical engineers did not define flight as "flying so like a pigeon that other pigeons are fooled"; they
studied aerodynamics. AI, likewise, studies the principles of acting well.

**Behaviour may not be understanding.** John Searle's **Chinese room** argument (1980) imagines a person who knows
no Chinese, locked in a room with a rule book. Chinese questions come in through a slot; the person follows the rules
to manipulate the symbols and passes out Chinese answers that native speakers find perfect. Searle argues that the
person does not understand Chinese, and neither, therefore, does a computer running the same rules. Many replies have
been published (the most common: the whole system of person plus rule book understands, even if the person does
not). There is no consensus. For this book the debate is useful mostly as a reminder that "passes a test" and
"understands" are different claims, and that we should say which one we mean.

**Better tests probe specific abilities.** Hector Levesque proposed the **Winograd schema** challenge (2011): pairs
of sentences such as "The trophy doesn't fit into the brown suitcase because *it* is too large / too small. What is
too large / small?" Changing one word flips the answer, and resolving "it" needs everyday knowledge of sizes and
containers, not tricks. Modern language models do well on such benchmarks, which raised a new, honest worry: did they
learn the knowledge, or patterns in how benchmark sentences are written? Chapter 17 returns to evaluation and its
pitfalls.

### Build it: a tiny ELIZA

Weizenbaum's program had a **script** (the best known was DOCTOR) of **keywords**, each with a rank, and for each
keyword a list of **decomposition patterns** and **reassembly rules**. To reply to an input, it:

1. finds the keywords in the input and picks the highest-ranked one;
2. tries that keyword's patterns in order; a pattern such as `* i am *` matches "well i am very unhappy today",
   with the first star matching `well` and the second `very unhappy today`;
3. **reflects** the matched pieces, swapping first and second person (`my` becomes `your`, `i` becomes `you`);
4. pastes them into the next reassembly template for that pattern, such as "How long have you been {2}?", cycling
   through the templates so that it does not repeat itself;
5. if no keyword matches, says something neutral, such as "Please go on."

Pattern matching with stars is a small search problem: each star can swallow any number of words, so the matcher
tries every split, shortest first, and backtracks if the rest of the pattern fails (backtracking is the subject of
[Chapter 14 of the Algorithms book](../algorithms/14-Backtracking-and-Branch-and-Bound.md)). The whole program:

```python
--8<-- "books/ai/ch01_eliza.py"
```

Output:

```
pattern match '* i am *' on 'well i am very unhappy today':
  stars -> [['well'], ['very', 'unhappy', 'today']]
reflect 'my plans and me' -> your plans and you

> Men are all alike.
  Please go on.   [keyword: None]
> They're always bugging us about something.
  Can you think of a specific example?   [keyword: always]
> Well, my father made me come here.
  Your father made you come here?   [keyword: father]
> I am unhappy about my work.
  How long have you been unhappy about your work?   [keyword: i]
> I want a quieter office.
  What would it mean to you if you got a quieter office?   [keyword: i]
> Because the computer room is noisy.
  Do computers worry you?   [keyword: computer]
> I feel nobody listens to me.
  Do you often feel nobody listens to you?   [keyword: i]
> The weather on Mars is cold.
  I see.   [keyword: None]
> I am unhappy about my work.
  Do you believe it is normal to be unhappy about your work?   [keyword: i]
```

The first three inputs are adapted from the sample conversation in Weizenbaum's 1966 paper. Trace one reply by
hand. For "Because the computer room is noisy." the words are `because the computer room is noisy`. Two keywords
occur: `because` (rank 2) and `computer` (rank 4). The higher rank wins. Its only pattern is `*`, which matches
everything, and its first template is "Do computers worry you?". For "I feel nobody listens to me." the keyword is
`i` (rank 1). Its patterns are tried in order: `* i am *` fails (there is no `am`), `* i want *` fails, `* i feel *`
matches with stars `[]` and `['nobody', 'listens', 'to', 'me']`; reflection turns the second into "nobody listens to
you", and the template "Do you often feel {2}?" gives the reply.

Notice what is missing. The program knows nothing about fathers, offices or Mars. The reply about Mars is a filler
because no keyword matched. When the same sentence comes back at the end, the reply changes only because a counter
moved on to the next template. And yet the conversation reads, for a few lines, like someone listening. That gap
between how a system *seems* and how it *works* is the first lesson of AI history, and it is why every program in
this book is built from the inside.

## 1.3 A short honest history

AI's history is often told as a story of geniuses, breakthroughs and betrayals. The real story is messier and more
interesting: a few ideas tried again and again, each succeeding on some problems and failing on others, with funding
and fashion swinging between them. Here is a compressed version, with dates and claims you can check in the sources
listed at the end. The history of machine learning in particular is told in
[Section 1.7 of the Machine learning book](../machine-learning/01-What-Is-Machine-Learning.md#17-a-short-honest-history),
so it is kept short here.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 260" role="img" aria-label="A timeline from 1940 to 2025. Above the axis: 1943 McCulloch and Pitts neurons, 1950 Turing's paper, 1956 Dartmouth workshop and Logic Theorist, 1966 ELIZA, 1970s expert systems such as MYCIN, 1986 backpropagation popularised, 1997 Deep Blue, 2012 AlexNet, 2017 transformer, 2020 GPT-3. Shaded bands mark the two periods called AI winters, mid 1970s and late 1980s to early 1990s.">
  <rect x="200" y="40" width="30" height="170" fill="#9cc9ea" fill-opacity="0.35"/>
  <text x="215" y="232" font-size="11" text-anchor="middle" fill="currentColor">winter</text>
  <rect x="265" y="40" width="30" height="170" fill="#9cc9ea" fill-opacity="0.35"/>
  <text x="280" y="232" font-size="11" text-anchor="middle" fill="currentColor">winter</text>
  <line x1="30" y1="210" x2="620" y2="210" stroke="currentColor" stroke-width="1.5"/>
  <text x="30" y="250" font-size="11" text-anchor="middle" fill="currentColor">1940</text>
  <text x="130" y="250" font-size="11" text-anchor="middle" fill="currentColor">1960</text>
  <text x="230" y="250" font-size="11" text-anchor="middle" fill="currentColor">1980</text>
  <text x="330" y="250" font-size="11" text-anchor="middle" fill="currentColor">2000</text>
  <text x="430" y="250" font-size="11" text-anchor="middle" fill="currentColor">2020</text>
  <line x1="30" y1="205" x2="30" y2="215" stroke="currentColor"/>
  <line x1="130" y1="205" x2="130" y2="215" stroke="currentColor"/>
  <line x1="230" y1="205" x2="230" y2="215" stroke="currentColor"/>
  <line x1="330" y1="205" x2="330" y2="215" stroke="currentColor"/>
  <line x1="430" y1="205" x2="430" y2="215" stroke="currentColor"/>
  <circle cx="45" cy="210" r="4" fill="#eea66f"/>
  <line x1="45" y1="206" x2="45" y2="190" stroke="currentColor" stroke-opacity="0.5"/>
  <text x="45" y="185" font-size="11" text-anchor="middle" fill="currentColor">1943 neurons</text>
  <circle cx="80" cy="210" r="4" fill="#eea66f"/>
  <line x1="80" y1="206" x2="80" y2="160" stroke="currentColor" stroke-opacity="0.5"/>
  <text x="80" y="155" font-size="11" text-anchor="middle" fill="currentColor">1950 Turing</text>
  <circle cx="110" cy="210" r="4" fill="#eea66f"/>
  <line x1="110" y1="206" x2="110" y2="130" stroke="currentColor" stroke-opacity="0.5"/>
  <text x="110" y="125" font-size="11" text-anchor="middle" fill="currentColor">1956 Dartmouth</text>
  <circle cx="160" cy="210" r="4" fill="#eea66f"/>
  <line x1="160" y1="206" x2="160" y2="100" stroke="currentColor" stroke-opacity="0.5"/>
  <text x="160" y="95" font-size="11" text-anchor="middle" fill="currentColor">1966 ELIZA</text>
  <circle cx="205" cy="210" r="4" fill="#eea66f"/>
  <line x1="205" y1="206" x2="205" y2="70" stroke="currentColor" stroke-opacity="0.5"/>
  <text x="205" y="65" font-size="11" text-anchor="middle" fill="currentColor">1970s expert systems</text>
  <circle cx="260" cy="210" r="4" fill="#eea66f"/>
  <line x1="260" y1="206" x2="260" y2="160" stroke="currentColor" stroke-opacity="0.5"/>
  <text x="260" y="155" font-size="11" text-anchor="middle" fill="currentColor">1986 backprop</text>
  <circle cx="315" cy="210" r="4" fill="#eea66f"/>
  <line x1="315" y1="206" x2="315" y2="130" stroke="currentColor" stroke-opacity="0.5"/>
  <text x="315" y="125" font-size="11" text-anchor="middle" fill="currentColor">1997 Deep Blue</text>
  <circle cx="390" cy="210" r="4" fill="#7ccf9a"/>
  <line x1="390" y1="206" x2="390" y2="160" stroke="currentColor" stroke-opacity="0.5"/>
  <text x="390" y="155" font-size="11" text-anchor="middle" fill="currentColor">2012 AlexNet</text>
  <circle cx="415" cy="210" r="4" fill="#7ccf9a"/>
  <line x1="415" y1="206" x2="415" y2="100" stroke="currentColor" stroke-opacity="0.5"/>
  <text x="440" y="95" font-size="11" text-anchor="middle" fill="currentColor">2017 transformer</text>
  <circle cx="430" cy="210" r="4" fill="#7ccf9a"/>
  <line x1="430" y1="206" x2="430" y2="130" stroke="currentColor" stroke-opacity="0.5"/>
  <text x="470" y="125" font-size="11" text-anchor="middle" fill="currentColor">2020 GPT-3</text>
  <text x="540" y="190" font-size="11" text-anchor="middle" fill="currentColor">orange: symbolic and</text>
  <text x="540" y="205" font-size="11" text-anchor="middle" fill="currentColor">early statistical era</text>
  <text x="540" y="160" font-size="11" text-anchor="middle" fill="currentColor">green: deep learning era</text>
</svg>
<figcaption>Figure 1.3. A few landmarks of AI on one axis (five pixels per year). The shaded bands mark the two
periods usually called "AI winters", roughly the mid 1970s and the late 1980s to early 1990s; their exact edges are
a matter of judgement.</figcaption>
</figure>

### Before the name (1943 to 1955)

Three lines of work came together. In 1943 Warren McCulloch and Walter Pitts described a simplified model of a
neuron as a threshold unit and showed that networks of such units could compute logical functions. In 1936 Turing
had defined the universal machine, and in 1950 he wrote the paper of Section 1.2. In 1950 C. E. Shannon published
"Programming a computer for playing chess", which laid out the idea of searching a game tree with an evaluation
function, the plan that chess programs followed for the next fifty years (Chapter 6). Arthur Samuel, at IBM, wrote a
checkers program in the early 1950s that later learned to play better than he did; his 1959 paper popularised the
phrase "machine learning".

### Dartmouth (1955 and 1956)

On 31 August 1955, John McCarthy (Dartmouth College), Marvin Minsky (Harvard), Nathaniel Rochester (IBM) and C. E.
Shannon (Bell Labs) wrote "A Proposal for the Dartmouth Summer Research Project on Artificial Intelligence". It is
the first known use of the phrase "artificial intelligence". The proposal asked for a two-month, ten-man study in the
summer of 1956, "to proceed on the basis of the conjecture that every aspect of learning or any other feature of
intelligence can in principle be so precisely described that a machine can be made to simulate it." It listed
topics that are still on the research agenda: programming computers to use language, neural networks, the theory of
how much computation a problem needs, self-improvement, abstraction, and randomness and creativity. It also
predicted that "a significant advance can be made" if a carefully chosen group "work on it together for a summer."
The workshop took place; the advance took longer.

### Early programs and great expectations (1956 to the early 1970s)

The most impressive program at the time of the workshop was the **Logic Theorist** of Allen Newell, Herbert Simon
and Cliff Shaw (1956), which proved theorems of propositional logic from Chapter 2 of Whitehead and Russell's
*Principia Mathematica* by searching through possible proof steps. Newell and Simon followed it with the **General
Problem Solver** (GPS, 1959), which used **means-ends analysis**: compare the current state with the goal, pick an
operator that reduces the difference, and recurse. Both are search programs in the sense of Chapter 3.

Other milestones: McCarthy designed the programming language **Lisp** (1958; paper 1960), which became AI's main
language for decades. Herbert Gelernter's geometry theorem prover (1959) proved school geometry theorems. Frank
Rosenblatt's **perceptron** (1958) learned to classify simple patterns. Daniel Bobrow's STUDENT (1964) solved
algebra word problems. **ELIZA** (1966) we built above. Terry Winograd's **SHRDLU** (around 1970) carried on typed
conversations about a simulated table of blocks, moving them on command and answering questions about them. At the
Stanford Research Institute (SRI), the robot **Shakey** (1966 to 1972) combined a camera, a planner and motion; the
project produced the A\* search algorithm (Hart, Nilsson and Raphael, 1968; Chapter 4) and the STRIPS planner
(Fikes and Nilsson, 1971; Chapter 10).

These programs worked on **microworlds**: small, clean, fully described domains such as a block table or a page of
algebra. Their authors expected that scaling up would be a matter of more facts and faster computers. Simon and
Newell predicted in 1958 that within ten years a computer would be the world chess champion; it took about forty.

### Combinatorial explosion and the first winter (the 1970s)

Scaling up failed for a reason that the theory of computation was just then making precise. Most of these programs
searched, and the number of possibilities grows exponentially with the size of the problem: a search that is
instant with 10 objects can take years with 30. Stephen Cook's 1971 paper on NP-completeness
([Chapter 22 of the Algorithms book](../algorithms/22-NP-Completeness.md)) showed that many search problems are
equivalent in difficulty, and that no clever trick was known for any of them. In Britain, the Lighthill report of
1973 judged that AI had not delivered on its promises, citing combinatorial explosion, and research funding there
was cut sharply. In the United States, funding for open-ended AI research was also reduced in the mid 1970s.
Separately, Minsky and Papert's book *Perceptrons* (1969) proved that a single-layer perceptron cannot compute some
simple functions (such as exclusive-or), and research on neural networks slowed for over a decade. This period of
reduced funding and interest is called the first **AI winter**.

### Knowledge is power: expert systems (the 1970s and 1980s)

The response was to stop seeking general methods and instead pack a lot of **specialist knowledge** into a program
for one narrow domain. DENDRAL (Stanford, from 1965; Feigenbaum, Buchanan and Lederberg) inferred the structure of
molecules from mass-spectrometer data, using rules that encoded chemists' expertise. **MYCIN** (Stanford, 1970s;
Shortliffe, Buchanan) recommended antibiotics for blood infections with a few hundred IF-THEN rules, each tagged with
a **certainty factor**. A blinded evaluation published in 1979 (Yu and colleagues) found its therapy recommendations
judged about as acceptable as those of the infectious-disease specialists compared with it; it was never used
routinely in hospitals. R1, later called XCON (McDermott, 1982), configured orders for DEC's VAX computers and was
used in production. In the early 1980s an industry grew up around **expert systems** and around special computers
for running Lisp. Japan launched its Fifth Generation Computer project (1982) built around logic programming.

What did an expert system look like inside? A **knowledge base** of rules, a **working memory** of facts about the
current case, and an **inference engine** that fires rules whose conditions hold. Here is one, small enough to read
in a minute. It identifies a rock from observations, with rules that are simplified textbook geology written for the
demonstration. Each rule has a certainty factor (CF) between 0 and 1; when a rule fires, its conclusion gets the
rule's CF times the smallest CF among its conditions, and two pieces of evidence for the same conclusion combine by
MYCIN's formula for positive factors,

$$
\mathrm{CF}(a, b) = a + b(1 - a) = 1 - (1 - a)(1 - b).
$$

The second form shows why this is sensible: $1 - a$ is the "remaining doubt" after the first rule, and each new
rule removes a fraction of what remains. It also shows the formula is commutative and associative, so the order in
which evidence for one conclusion arrives does not matter. (MYCIN had separate formulas for negative evidence;
they are in the program.)

```python
--8<-- "books/ai/ch01_expert_system.py"
```

Output:

```
combine(0.56, 0.42) = 0.7448

case: dark, fine-grained, with gas holes
    rule 1 fires: type=volcanic gets 0.560 -> now 0.560
    rule 2 fires: type=volcanic gets 0.420 -> now 0.745
    rule 5 fires: rock=basalt gets 0.596 -> now 0.596
  conclusion rock=basalt with CF 0.596

case: light, coarse-grained
    rule 3 fires: type=plutonic gets 0.630 -> now 0.630
    rule 6 fires: rock=granite gets 0.504 -> now 0.504
  conclusion rock=granite with CF 0.504

case: layered, sand grains visible, medium grain
    rule 4 fires: type=sedimentary gets 0.720 -> now 0.720
    rule 7 fires: rock=sandstone gets 0.504 -> now 0.504
  conclusion rock=sandstone with CF 0.504

case: glassy and green (no rule mentions it)
  no conclusion: the rules do not cover this case
```

Trace the first case. The facts are colour dark (CF 1.0), grain fine (0.8), gas holes, called vesicles (0.7). Rule
1 needs dark and fine: it fires with $0.7 \times \min(1.0, 0.8) = 0.56$ for "volcanic". Rule 2 needs vesicles: it
gives $0.6 \times 0.7 = 0.42$ more evidence for "volcanic", and the two combine to
$0.56 + 0.42 \times 0.44 = 0.7448$. Rule 5 needs volcanic and dark: $0.8 \times \min(0.7448, 1.0) = 0.596$ for basalt. (The basaltic rocks of
the Martian surface are a real-world case where the first rule would fire a lot.)

The last case shows the weakness that sank the expert-system industry. A rock the rule writer did not think of gets
no answer at all, not even "I am not sure". Real expert systems failed the same way at the edges of their domain,
and each new kind of case needed a human expert and a "knowledge engineer" to write more rules, which then
interacted with the old ones in ways that were hard to predict (exercise 5 shows an interaction in this tiny
system). This difficulty was called the **knowledge acquisition bottleneck**. The certainty factors, too, turned out
to lack a clear meaning: they behave like probabilities in some cases and not in others. In the late 1980s the
market for expert systems and Lisp machines collapsed, and a second winter followed.

### Uncertainty, learning and statistics (the late 1980s to the 2000s)

Two shifts came out of that failure. The first was to take **uncertainty** seriously with real probability theory.
Judea Pearl's book *Probabilistic Reasoning in Intelligent Systems* (1988) introduced Bayesian networks, which make
probabilistic reasoning tractable by writing down which variables directly influence which (Chapter 12). The second
was to **learn** knowledge from data rather than write it by hand. Backpropagation for training multi-layer neural
networks was popularised by Rumelhart, Hinton and Williams in 1986, overcoming the single-layer limits that Minsky and
Papert had proved. Speech recognition moved to **hidden Markov models** trained on recorded speech (Chapter 13), and
machine translation moved from hand-written grammar rules to statistical models learned from translated text (Brown
and colleagues at IBM, 1990). Reinforcement learning grew into a field (Sutton and Barto's textbook appeared in
1998). Methods were now judged by careful experiments on shared data sets, which made the field more like an
experimental science.

Results followed in narrow but hard domains. In 1997 IBM's Deep Blue beat the world chess champion Garry Kasparov
in a six-game match, by search and a hand-tuned evaluation function on special hardware (Chapter 6). In 2005 the
Stanford car Stanley won the DARPA Grand Challenge, driving a desert course of over 200 km with no human control;
in the 2004 challenge no car had finished. Stanley combined probabilistic sensing with machine learning (Thrun and
colleagues, 2006).

### Deep learning (from 2012)

Neural networks with many layers had been studied for decades, but three things came together around 2010: large
labelled data sets (ImageNet, with over a million labelled images), fast parallel hardware (graphics processors),
and training techniques that worked for deep networks. In 2012 a convolutional network by Krizhevsky, Sutskever and
Hinton, now called AlexNet, won the ImageNet image-classification challenge with a top-5 error of 15.3 percent,
against 26.2 percent for the second-best entry, as reported in their paper. Within a few years deep learning
dominated computer vision, speech recognition and machine translation. The
[Machine learning book](../machine-learning/01-What-Is-Machine-Learning.md) builds these networks from scratch.

Deep learning also combined with search. **AlphaGo** (Silver and colleagues, 2016) used neural networks to guide
Monte Carlo tree search and beat top professional players at Go, a game whose search tree is far too large for the
Deep Blue approach; AlphaZero (2018) learned chess, shogi and Go from self-play alone (Chapter 6). **AlphaFold 2**
(Jumper and colleagues, 2021) predicted the 3-D structures of proteins with accuracy that, in the CASP14 assessment,
was often comparable to experimental methods.

### Language models (from 2017)

The **transformer** architecture ("Attention Is All You Need", Vaswani and colleagues, 2017) made it practical to
train very large networks on text to predict the next word. GPT-3 (Brown and colleagues, 2020), with 175 billion
parameters, showed that such a model could perform tasks it was not explicitly trained for when given a few examples
in its input ("few-shot" prompting). Fine-tuning with human feedback (Ouyang and colleagues, 2022) made these models
follow instructions in conversation. Chapter 17 explains how they work and what is and is not known about them.

### What the history teaches

Four patterns repeat, and are worth keeping in mind when reading claims about AI today.

1. **Demonstrations on small, clean problems overstate progress on messy ones.** Microworlds in the 1960s, expert
   systems in the 1980s, benchmarks today.
2. **Search alone hits combinatorial explosion; knowledge alone hits the acquisition bottleneck.** Many of the big
   successes (Deep Blue, AlphaGo, modern planners) combine search with knowledge, increasingly learned knowledge.
3. **Methods return.** Neural networks were proposed in 1943, dismissed in 1969, revived in 1986, sidelined in the
   1990s and dominant after 2012. Logic and search, out of fashion in some years, run inside today's SAT solvers,
   planners and verification tools.
4. **Prediction dates are unreliable.** Simon and Newell's ten-year chess forecast took about forty; Turing's fifty-year forecast for
   his game was roughly right in some readings and wrong in others. This book makes no forecasts.

## 1.4 Narrow and general AI

*Level: beginner to intermediate.*

Deep Blue could beat the world chess champion and could not play tic-tac-toe; nobody had programmed it to. A system
built for one task (or a family of closely related tasks) is called **narrow** AI. A system that could learn and
perform the whole range of intellectual tasks a person can, and carry knowledge from one to the next, would be
**general** AI, often written AGI (artificial general intelligence). Almost every deployed AI system is narrow:
spam filters, route planners, face unlocking, recommendation, speech-to-text, protein structure prediction.

Large language models blur the line, because one model can translate, summarise, write code, answer questions and
play word games. They are more general than any earlier system. Whether they are on a path to general intelligence
is a question researchers disagree about, and evidence on both sides is still being collected; this book does not
take a side. What we can do is list what is documented.

### What current systems do well

These claims are each backed by a published paper or competition result:

- **Perception on benchmarks.** Image classification, speech recognition and object detection reach or exceed the
  accuracy of human labellers on standard test sets.
- **Games with clear rules.** Chess, Go, shogi (AlphaZero, Silver and colleagues, 2018), poker variants (Libratus,
  Brown and Sandholm, 2018) and some video games at top human level.
- **Search, optimisation and logic at scale.** Route planners on continent-sized road maps answer in milliseconds;
  SAT solvers (Chapter 8) settle industrial problems with millions of variables; planners schedule spacecraft
  (Chapter 10).
- **Scientific prediction in specific domains.** Protein structure (AlphaFold 2, 2021).
- **Fluent text and code.** Language models write grammatical, relevant text in many languages and produce working
  code for many routine programming tasks.

### What they do not do, or do unreliably

These limits are also documented, and they recur across systems:

- **Brittleness under distribution shift.** A model trained on one kind of data can fail on slightly different
  data. Recht and colleagues (2019) built a new test set for ImageNet following the original procedure as closely as
  they could, and found that accuracy of the models they tested fell by about 11 to 14 percentage points.
- **Adversarial examples.** Tiny, carefully chosen changes to an input, invisible to people, can change a neural
  network's answer (Szegedy and colleagues, 2014).
- **Shortcuts.** Networks often learn a cue that happens to correlate with the label in training data (a background,
  a watermark) instead of the intended concept (Geirhos and colleagues, 2020).
- **Confident errors.** Language models state false things fluently ("hallucination"), and many classifiers are
  overconfident in their probabilities (Chapter 20).
- **Unreliable reasoning and planning.** Language models fail on some problems that need many steps of exact
  reasoning or planning, especially when the problem is reworded away from familiar forms; Valmeekam and colleagues
  (2023) measured this on classical planning problems, and Berglund and colleagues (2023) found models trained on
  "A is B" often fail to answer "what is B?".
- **Physical common sense and dexterity.** Picking up an unfamiliar object or folding laundry remains hard for
  robots, though easy for a child. Hans Moravec observed in 1988 that the skills people find hard (chess, algebra)
  were easier for computers than the skills people find effortless (seeing, walking, grasping). This is called
  **Moravec's paradox**; it has softened for perception, but much less for manipulation.

A useful habit when you meet a claim about an AI system: ask *what exactly was measured, on what data, compared
with what*. A score on a benchmark is a measurement of the benchmark. Chapter 17 (Section 17.6) and Chapter 20
(Section 20.7) are about doing this well.

### Strong and weak AI

Philosophers use two older terms. **Weak AI** is the claim that machines can act *as if* they were intelligent.
**Strong AI** is the claim that a suitably programmed machine would *actually* have a mind, with understanding and
perhaps consciousness. Searle's Chinese room was aimed at strong AI. These are not the same as narrow and general:
a general system could exist without settling the strong AI question. This book is about engineering, so it works
with weak AI throughout: we build agents that act well, and we measure how well.

## 1.5 The map of this book

The book follows one idea: an **agent** that perceives, decides and acts, made a little more capable in each part.
The Machine learning book ([../machine-learning/](../machine-learning/01-What-Is-Machine-Learning.md)) covers
learning methods in depth; this book links to it rather than repeating it, and focuses on how agents reason, plan
and decide, and how learning fits in. The Algorithms book ([../algorithms/](../algorithms/01-What-Is-an-Algorithm.md))
covers the graph algorithms and data structures that search relies on.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 250" role="img" aria-label="The five parts of the book as a chain of boxes: Part I what AI is and agents, chapters 1 and 2; Part II search, chapters 3 to 7; Part III knowledge, logic and planning, chapters 8 to 11; Part IV uncertainty, chapters 12 to 14; Part V learning agents and beyond, chapters 15 to 21. Arrows show that each part builds on the one before.">
  <rect x="10" y="60" width="110" height="110" rx="8" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor"/>
  <text x="65" y="90" font-size="13" font-weight="bold" text-anchor="middle" fill="currentColor">Part I</text>
  <text x="65" y="112" font-size="12" text-anchor="middle" fill="currentColor">what AI is;</text>
  <text x="65" y="130" font-size="12" text-anchor="middle" fill="currentColor">agents</text>
  <text x="65" y="155" font-size="11" text-anchor="middle" fill="currentColor">ch. 1-2</text>
  <rect x="137" y="60" width="110" height="110" rx="8" fill="#eea66f" fill-opacity="0.35" stroke="currentColor"/>
  <text x="192" y="90" font-size="13" font-weight="bold" text-anchor="middle" fill="currentColor">Part II</text>
  <text x="192" y="112" font-size="12" text-anchor="middle" fill="currentColor">search, games,</text>
  <text x="192" y="130" font-size="12" text-anchor="middle" fill="currentColor">constraints</text>
  <text x="192" y="155" font-size="11" text-anchor="middle" fill="currentColor">ch. 3-7</text>
  <rect x="264" y="60" width="110" height="110" rx="8" fill="#eea66f" fill-opacity="0.35" stroke="currentColor"/>
  <text x="319" y="90" font-size="13" font-weight="bold" text-anchor="middle" fill="currentColor">Part III</text>
  <text x="319" y="112" font-size="12" text-anchor="middle" fill="currentColor">logic, planning,</text>
  <text x="319" y="130" font-size="12" text-anchor="middle" fill="currentColor">knowledge</text>
  <text x="319" y="155" font-size="11" text-anchor="middle" fill="currentColor">ch. 8-11</text>
  <rect x="391" y="60" width="110" height="110" rx="8" fill="#7ccf9a" fill-opacity="0.4" stroke="currentColor"/>
  <text x="446" y="90" font-size="13" font-weight="bold" text-anchor="middle" fill="currentColor">Part IV</text>
  <text x="446" y="112" font-size="12" text-anchor="middle" fill="currentColor">probability,</text>
  <text x="446" y="130" font-size="12" text-anchor="middle" fill="currentColor">time, decisions</text>
  <text x="446" y="155" font-size="11" text-anchor="middle" fill="currentColor">ch. 12-14</text>
  <rect x="518" y="60" width="112" height="110" rx="8" fill="#7ccf9a" fill-opacity="0.4" stroke="currentColor"/>
  <text x="574" y="90" font-size="13" font-weight="bold" text-anchor="middle" fill="currentColor">Part V</text>
  <text x="574" y="112" font-size="12" text-anchor="middle" fill="currentColor">learning agents</text>
  <text x="574" y="130" font-size="12" text-anchor="middle" fill="currentColor">and beyond</text>
  <text x="574" y="155" font-size="11" text-anchor="middle" fill="currentColor">ch. 15-21</text>
  <line x1="120" y1="115" x2="131" y2="115" stroke="currentColor" stroke-width="1.5"/>
  <polygon points="137,115 130,111 130,119" fill="currentColor"/>
  <line x1="247" y1="115" x2="258" y2="115" stroke="currentColor" stroke-width="1.5"/>
  <polygon points="264,115 257,111 257,119" fill="currentColor"/>
  <line x1="374" y1="115" x2="385" y2="115" stroke="currentColor" stroke-width="1.5"/>
  <polygon points="391,115 384,111 384,119" fill="currentColor"/>
  <line x1="501" y1="115" x2="512" y2="115" stroke="currentColor" stroke-width="1.5"/>
  <polygon points="518,115 511,111 511,119" fill="currentColor"/>
  <text x="320" y="30" font-size="13" text-anchor="middle" fill="currentColor">known world, exact answers  →  uncertain world, learned behaviour</text>
  <text x="320" y="210" font-size="12" text-anchor="middle" fill="currentColor">orange: the world is known and certain; green: the agent must handle</text>
  <text x="320" y="228" font-size="12" text-anchor="middle" fill="currentColor">uncertainty and learn from experience</text>
</svg>
<figcaption>Figure 1.4. The five parts of the book. Early parts assume the agent knows exactly how the world works;
later parts remove that assumption step by step.</figcaption>
</figure>

**Part I. What AI is.** This chapter, and [Chapter 2](02-Intelligent-Agents.md) on agents and environments: the
vocabulary for everything that follows, with five kinds of agent coded in a grid world.

**Part II. Problem solving by search.** When the agent knows the rules of its world, it can plan by searching
ahead. [Chapter 3](03-Uninformed-Search.md) searches blindly (breadth-first, depth-first, iterative deepening);
[Chapter 4](04-Heuristic-Search.md) uses estimates to search towards the goal (A\*);
[Chapter 5](05-Local-Search-and-Optimization.md) improves a single candidate instead of building a path;
[Chapter 6](06-Games-and-Adversarial-Search.md) searches against an opponent; and
[Chapter 7](07-Constraint-Satisfaction.md) exploits the structure of constraint problems such as timetables and
Sudoku.

**Part III. Knowledge, logic and planning.** Agents that represent what they know as statements and reason with
them: [Chapter 8](08-Propositional-Logic-and-SAT.md) (propositional logic and SAT solvers),
[Chapter 9](09-First-Order-Logic.md) (first-order logic), [Chapter 10](10-Planning.md) (automated planning, as
used on spacecraft) and [Chapter 11](11-Knowledge-Representation.md) (how to organise knowledge).

**Part IV. Uncertainty.** Agents that do not know the world exactly:
[Chapter 12](12-Probabilistic-Reasoning.md) (Bayesian networks), [Chapter 13](13-Reasoning-over-Time.md) (tracking
a changing world: hidden Markov models, Kalman and particle filters) and [Chapter 14](14-Making-Decisions.md)
(utility and Markov decision processes).

**Part V. Learning agents.** Agents that improve from experience and the frontier:
[Chapter 15](15-Reinforcement-Learning.md) (reinforcement learning),
[Chapter 16](16-Natural-Language-Processing.md) (language), [Chapter 17](17-Large-Language-Models.md) (large
language models), [Chapter 18](18-Perception-and-Robotics.md) (perception and robotics, including the real
autonomy of Mars rovers), [Chapter 19](19-Multi-Agent-Systems.md) (many agents: game theory),
[Chapter 20](20-Safe-and-Reliable-AI.md) (safety and reliability, treated technically) and
[Chapter 21](21-Where-AI-Goes.md) (open problems).

**How to read it.** Every chapter has the same shape: a question, the ideas built from scratch, proofs of why they
work, runnable Python (with NumPy from Chapter 12 on, where vectors help), and exercises with full answers. Code
listings are complete programs: copy one, run it with `python3`, and you should see the printed output shown under
it. Sections marked *advanced* or *expert* can be skipped on a first reading without losing the thread.

## Check yourself

??? question "1. Classify each of these into one of the four families of Figure 1.1: (a) a program judged by whether its error patterns on memory tasks match human subjects; (b) a theorem prover judged by whether every conclusion follows from its axioms; (c) a chatbot judged by whether users think it is human; (d) a delivery robot judged by on-time, undamaged deliveries."

    (a) Thinking humanly: the inner process is compared with human cognition. (b) Thinking rationally: the inner
    process is judged by the standard of correct inference. (c) Acting humanly: only behaviour matters, measured
    against people. (d) Acting rationally: only behaviour matters, measured by a performance measure that has
    nothing to do with resembling a person.

??? question "2. Why does Turing's sample dialogue have the machine pause and give a wrong answer to an addition? What does that tell you about the test?"

    In the imitation game the machine wins by being mistaken for a person. A person adding 34957 and 70764 in their
    head takes time and might slip; an instant, perfect answer would give the machine away. (The correct sum is
    105721; Turing's imagined machine answers 105621 after about 30 seconds.) So the test rewards imitating human
    limitations, not just intelligence: it is a test of human-likeness. That is one reason AI research measures
    specific abilities against performance measures instead.

??? question "3. In the ELIZA program, what reply does it give to \"My mother cooks for me\", and why? Trace the matching."

    The words are `my mother cooks for me`. The only keyword is `mother` (rank 3). Its pattern `* my mother *`
    matches with the first star `[]` and the second star `['cooks', 'for', 'me']`. This is the first use of that
    pattern, so the template is the first one, "Tell me more about your family.", which uses no stars. The reply
    is "Tell me more about your family." A second "my mother ..." sentence would get the second template, "Who else
    in your family {2}?", with the second star reflected (for this input it would be "Who else in your family cooks
    for you?").

??? question "4. Show that for positive certainty factors the combination $a + b(1-a)$ equals $1 - (1-a)(1-b)$, and deduce that it is commutative and associative and stays below 1. Compute the combined CF of three rules giving 0.3, 0.5 and 0.4."

    Expand: $1 - (1-a)(1-b) = 1 - (1 - a - b + ab) = a + b - ab = a + b(1-a)$. In the product form, swapping $a$
    and $b$ changes nothing, so it is commutative. Combining three factors in either grouping gives
    $1 - (1-a)(1-b)(1-c)$, so it is associative. If $a, b < 1$ the product $(1-a)(1-b)$ is positive, so the result is below 1.
    For 0.3, 0.5 and 0.4: $1 - 0.7 \times 0.5 \times 0.6 = 1 - 0.21 = 0.79$. The program agrees:
    `combine(combine(0.3, 0.5), 0.4)` and `combine(0.3, combine(0.5, 0.4))` both print 0.79 (up to rounding).

??? question "5. In the expert system, move rule 5 (volcanic and dark gives basalt) to second place in the list. What CF does the first case get for basalt now, and why is this a problem?"

    The forward chainer fires rules in list order and fires each rule only once. Now the order is rule 1
    (volcanic gets 0.56), then the basalt rule: $0.8 \times \min(0.56, 1.0) = 0.448$, then the vesicle rule raises
    volcanic to 0.7448. But the basalt rule has already fired and is not fired again, so basalt stays at 0.448,
    instead of 0.596 with the original order. Running `infer` with the rule moved gives
    `{'rock=basalt': 0.448}` (up to rounding). The answer depends on the order the rules were typed in, which no geologist intended. Real systems
    needed careful control strategies (and still had surprises); it is one face of why large rule bases were hard to
    maintain. A fix is to re-fire a rule whenever the CF of one of its conditions changes, which needs care to
    avoid counting the same evidence twice.

??? question "6. Is a thermostat an agent? Is it a rational agent? Is it AI?"

    It is an agent: it perceives (temperature) and acts (switches the heater). It can be rational for a suitable
    performance measure: if the measure is "keep the room between 19 and 21 degrees with as little switching as
    possible", a thermostat with a little hysteresis does about the best possible with what it perceives. Whether to
    call it AI is a matter of taste; most people would not, because its behaviour is fixed and simple. The point
    of the rational-agent view is that the same concepts cover the thermostat and the Mars rover, and the
    interesting questions are about how hard the environment is (Chapter 2).

??? question "7. Write code: give the ELIZA a short memory. When an input contains \"my\" followed by some words and no keyword applies, store the reflected phrase; later, when no keyword matches, say \"Earlier you mentioned your ...\" instead of a filler."

    ```python
    from ch01_eliza import Eliza, words, reflect

    class MemoryEliza(Eliza):
        def __init__(self):
            super().__init__()
            self.memory = []

        def reply(self, text):
            ws = words(text)
            r, k = super().reply(text)
            recalled = None
            if k is None and self.memory:          # nothing matched: recall
                recalled = self.memory.pop(0)
            if "my" in ws:                          # remember "my ..." phrases
                self.memory.append(reflect(ws[ws.index("my"):]))
            if recalled:
                return f"Earlier you mentioned {recalled}.", "memory"
            return r, k

    e = MemoryEliza()
    for s in ["My plants keep dying.", "I am tired.", "It rained today."]:
        print(s, "->", e.reply(s)[0])
    ```

    Run next to `ch01_eliza.py`, this prints "Please go on." for the first line (no keyword, nothing in memory
    yet), "How long have you been tired?" for the second (keyword `i`), and "Earlier you mentioned your plants keep
    dying." for the third. Weizenbaum's ELIZA had a similar memory, attached to the keyword "my". The trick makes
    the program seem more attentive while adding no understanding at all.

??? question "8. The Dartmouth proposal asked for two months and ten people. Name two problems listed in the proposal that are still research topics, and one reason the summer could not deliver what was hoped."

    The proposal's topics included programming computers to use language, neural networks ("neuron nets"), how
    much computation a calculation needs, self-improvement, abstraction, and randomness and creativity. Using
    language and neural networks are both still active. One reason the hope failed: most of these problems need
    search through enormous spaces, and the combinatorial explosion (later explained by the theory of
    NP-completeness, Cook 1971) made methods that worked on small examples useless on large ones. A second: the
    amount of everyday knowledge needed was vastly underestimated.

??? question "9. Explain Moravec's paradox with one example from this chapter, and say in one sentence how deep learning changed it and where it still holds."

    The Logic Theorist proved logic theorems (hard for people) in 1956, while recognising a cup in a photograph
    (easy for a toddler) was beyond computers for another fifty years. Deep learning changed the perception half:
    trained on millions of examples, networks now recognise objects well on benchmarks. Physical manipulation of
    unfamiliar objects in messy surroundings is still hard for robots, so the paradox still holds there.

??? question "10. A news item says \"a new AI system beats doctors at diagnosis\". Write down four questions you would ask before believing it, using ideas from Section 1.4."

    (1) Which task exactly: what images or records, what diagnoses, and how was the "right answer" decided? (2)
    On what data was it tested, and was that data collected separately from the training data (distribution shift,
    contamination)? (3) Compared with which doctors, under what conditions (time, extra information doctors
    normally have)? (4) How does it fail: are its errors confident, does it say when it is unsure, and how does
    accuracy change on patients from other hospitals? A fifth good question: was the result published with enough
    detail for others to check it?

??? question "11. Searle's Chinese room is said to show that running the right program is not enough for understanding. State the \"systems reply\" and one response Searle gave to it."

    The systems reply: the person in the room is only a part (like a processor); the whole system, person plus
    rule book plus scratch paper, is what understands Chinese, so it is no surprise the part does not. Searle's
    response in the 1980 paper: let the person memorise the rule book and do everything in their head; now the
    person *is* the whole system, and still, Searle says, understands no Chinese. Critics reply that the memorised
    system could still be a distinct mind running on the person's brain. The debate is not settled; it is a
    disagreement about what "understanding" means, not about any experiment.

## What you learned

- AI has four families of definitions, from two questions: process or behaviour, human or rational standard. This
  book takes the rational-agent view: act to maximise expected performance given what you know.
- The performance measure is part of the definition, and a badly chosen one produces bad behaviour from a
  perfectly "rational" agent.
- Turing's imitation game turned "can machines think?" into an experiment, but it rewards human-likeness and can be
  gamed by tricks, as ELIZA showed; Searle's Chinese room and the Winograd schemas probe its limits.
- ELIZA works by keyword ranking, wildcard patterns and pronoun reflection, with no model of the world; a rule-based
  expert system works by forward chaining over IF-THEN rules with certainty factors, and is brittle outside its
  rules.
- The history alternates: early search programs hit combinatorial explosion; expert systems hit the knowledge
  bottleneck; probability and learning from data took over; deep learning and then language models scaled learning
  up; search and logic survive inside many of the strongest systems.
- Almost all AI is narrow. Current systems are strong on perception benchmarks, games, large-scale search and
  fluent text, and weak on distribution shift, adversarial inputs, confident errors, long exact reasoning and
  physical manipulation.

**Next:** [Chapter 2](02-Intelligent-Agents.md) makes "agent" and "environment" precise, and builds five kinds of
agent, from a simple reflex to a learner, in a small grid world.

## Further reading

- S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed., Pearson, 2020, Chapter 1 (the
  four approaches, foundations and history).
- A. M. Turing, "Computing machinery and intelligence", *Mind* 59(236), 1950.
- J. McCarthy, M. L. Minsky, N. Rochester and C. E. Shannon, "A proposal for the Dartmouth summer research project
  on artificial intelligence", 1955 (reprinted in *AI Magazine* 27(4), 2006).
- J. Weizenbaum, "ELIZA: a computer program for the study of natural language communication between man and
  machine", *Communications of the ACM* 9(1), 1966; and *Computer Power and Human Reason*, 1976.
- A. Newell and H. A. Simon, "The logic theory machine: a complex information processing system", *IRE Transactions
  on Information Theory* 2(3), 1956.
- C. E. Shannon, "Programming a computer for playing chess", *Philosophical Magazine* 41(314), 1950.
- W. S. McCulloch and W. Pitts, "A logical calculus of the ideas immanent in nervous activity", *Bulletin of
  Mathematical Biophysics* 5, 1943.
- E. H. Shortliffe, *Computer-Based Medical Consultations: MYCIN*, Elsevier, 1976; B. G. Buchanan and E. H.
  Shortliffe (eds.), *Rule-Based Expert Systems: The MYCIN Experiments of the Stanford Heuristic Programming
  Project*, Addison-Wesley, 1984.
- J. R. Searle, "Minds, brains, and programs", *Behavioral and Brain Sciences* 3(3), 1980.
- H. J. Levesque, E. Davis and L. Morgenstern, "The Winograd schema challenge", KR 2012.
- N. J. Nilsson, *The Quest for Artificial Intelligence: A History of Ideas and Achievements*, Cambridge University
  Press, 2010 (a careful history by one of the field's pioneers).
- A. Krizhevsky, I. Sutskever and G. E. Hinton, "ImageNet classification with deep convolutional neural networks",
  NeurIPS 2012.
- B. Recht, R. Roelofs, L. Schmidt and V. Shankar, "Do ImageNet classifiers generalize to ImageNet?", ICML 2019.
- H. Moravec, *Mind Children*, Harvard University Press, 1988.
- On this site: [Chapter 1 of the Machine learning book](../machine-learning/01-What-Is-Machine-Learning.md) (what
  learning is, and its history), [Chapter 1 of the Algorithms book](../algorithms/01-What-Is-an-Algorithm.md)
  (algorithms and Turing machines), and [backtracking](../../backtracking/subsets-permutations.md) (the technique
  ELIZA's matcher uses).
