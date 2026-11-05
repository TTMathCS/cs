# 1. What is machine learning?

*Some problems are easy to state and almost impossible to write rules for. Nobody can write down, step by step, how
to tell a photo of a cat from a photo of a dog, or which emails a person will call spam, yet people do these things
every day from experience. Machine learning is the craft of writing programs that get better at a task from
examples instead of from rules a person wrote. In this chapter you will see what that means precisely, meet the main
kinds of learning, build a complete first learner in about twenty lines of Python, learn why we always hide some
data from it, walk through the workflow that every project follows, see the hard limits of what learning can do, and
read a short, honest history of how the field got here.*

!!! abstract "In this chapter"
    **You will learn:**

    - what it means for a program to learn, with Mitchell's definition of task, experience and performance
    - the main kinds of learning: supervised (regression and classification), unsupervised, self-supervised and
      reinforcement learning
    - how to build a nearest-neighbour classifier from scratch and trace it by hand
    - why data is split into training, validation and test sets, and what goes wrong when it is not
    - the workflow of a machine-learning project, from the question to deployment
    - what learning cannot do: learn without data, find causes from correlations alone, or beat every other learner
      on every problem (the no-free-lunch theorem, proved in a small case)
    - where the field came from: Samuel's checkers, the perceptron, the winters and the 2012 ImageNet result

    **You need:** school algebra, the distance between two points from coordinate geometry, and the habit of reading
    a short Python program. [Chapter 1 of the Algorithms book](../algorithms/01-What-Is-an-Algorithm.md) explains
    what an algorithm is, if that word is new. The math books at
    [math.akadian.ca](https://math.akadian.ca/books/) are there for more practice; Chapter 3 of this book builds the
    rest of the math we need.

    **Levels:** 1.1 to 1.5 are beginner; 1.6 is beginner to intermediate (the no-free-lunch proof is intermediate);
    1.7 is for everyone.

## 1.1 Programs that learn from examples instead of rules

How would you write a program that tells lemons from oranges? A first try is to write rules. "If it is yellow, it is
a lemon." But some oranges are yellowish and some lemons are green. "If it is longer than it is wide, it is a lemon."
That is better, but a squashed orange is longer than it is wide too, and how much longer counts? Every rule you add
has exceptions, and every exception needs another rule. For lemons and oranges you might, with patience, get
somewhere. For "is there a pedestrian in this camera image" or "what is the next word in this sentence", writing the
rules by hand has been tried for decades and works badly.

Machine learning turns the problem around. Instead of writing the rules, we collect **examples**: many fruit, each
measured and each with the right answer written next to it. Then we write a *general* program, one that knows
nothing about fruit, whose job is to find a rule that fits the examples. That general program is called a **learning
algorithm** or **learner**. The rule it finds is called a **model**. Then we use the model on fruit it has never
seen.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 230" role="img" aria-label="Two pipelines. Top, ordinary programming: rules written by a person and input data go into a program, which produces answers. Bottom, machine learning: example inputs and their right answers go into a learning algorithm, which produces a model; the model then takes new inputs and produces answers.">
  <text x="20" y="28" font-size="14" font-weight="bold" fill="currentColor">ordinary programming</text>
  <rect x="20" y="40" width="130" height="34" rx="6" fill="#eea66f" fill-opacity="0.35" stroke="currentColor"/>
  <text x="85" y="62" font-size="13" text-anchor="middle" fill="currentColor">rules (by a person)</text>
  <rect x="20" y="82" width="130" height="34" rx="6" fill="#9cc9ea" fill-opacity="0.4" stroke="currentColor"/>
  <text x="85" y="104" font-size="13" text-anchor="middle" fill="currentColor">input data</text>
  <line x1="150" y1="57" x2="222" y2="74" stroke="currentColor" stroke-width="1.5"/>
  <line x1="150" y1="99" x2="222" y2="82" stroke="currentColor" stroke-width="1.5"/>
  <rect x="230" y="58" width="120" height="40" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="290" y="83" font-size="13" text-anchor="middle" fill="currentColor">program</text>
  <line x1="350" y1="78" x2="412" y2="78" stroke="currentColor" stroke-width="1.5"/>
  <polygon points="420,78 410,73 410,83" fill="currentColor"/>
  <rect x="422" y="61" width="110" height="34" rx="6" fill="#7ccf9a" fill-opacity="0.4" stroke="currentColor"/>
  <text x="477" y="83" font-size="13" text-anchor="middle" fill="currentColor">answers</text>
  <line x1="20" y1="132" x2="620" y2="132" stroke="currentColor" stroke-opacity="0.3"/>
  <text x="20" y="156" font-size="14" font-weight="bold" fill="currentColor">machine learning</text>
  <rect x="20" y="166" width="130" height="24" rx="6" fill="#9cc9ea" fill-opacity="0.4" stroke="currentColor"/>
  <text x="85" y="183" font-size="12" text-anchor="middle" fill="currentColor">example inputs</text>
  <rect x="20" y="196" width="130" height="24" rx="6" fill="#7ccf9a" fill-opacity="0.4" stroke="currentColor"/>
  <text x="85" y="213" font-size="12" text-anchor="middle" fill="currentColor">their right answers</text>
  <line x1="150" y1="178" x2="182" y2="190" stroke="currentColor" stroke-width="1.5"/>
  <line x1="150" y1="208" x2="182" y2="198" stroke="currentColor" stroke-width="1.5"/>
  <rect x="186" y="174" width="128" height="40" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="250" y="199" font-size="13" text-anchor="middle" fill="currentColor">learning algorithm</text>
  <line x1="314" y1="194" x2="356" y2="194" stroke="currentColor" stroke-width="1.5"/>
  <polygon points="364,194 354,189 354,199" fill="currentColor"/>
  <rect x="366" y="177" width="96" height="34" rx="6" fill="#eea66f" fill-opacity="0.35" stroke="currentColor"/>
  <text x="414" y="199" font-size="13" text-anchor="middle" fill="currentColor">model</text>
  <text x="414" y="168" font-size="11" text-anchor="middle" fill="currentColor">new input</text>
  <line x1="462" y1="194" x2="502" y2="194" stroke="currentColor" stroke-width="1.5"/>
  <polygon points="510,194 500,189 500,199" fill="currentColor"/>
  <rect x="512" y="177" width="110" height="34" rx="6" fill="#7ccf9a" fill-opacity="0.4" stroke="currentColor"/>
  <text x="567" y="199" font-size="13" text-anchor="middle" fill="currentColor">answers</text>
</svg>
<figcaption>Ordinary programming turns rules and data into answers. Machine learning turns examples (inputs with
their answers) into a model, and the model turns new inputs into answers. The rules are an output, not an
input.</figcaption>
</figure>

The learning algorithm is still an ordinary algorithm in the sense of the
[Algorithms book](../algorithms/01-What-Is-an-Algorithm.md): finite, definite steps from input to output. What is
new is its input and its output. Its input is a set of examples. Its output is itself a program, the model, which we
then run on new inputs. And its correctness is of a new kind. A sorting algorithm is correct if it sorts every list.
A learner cannot be "correct" in that sense, because the right answer on a fruit it has never seen is not determined
by the fruit it has seen. The best a learner can do is be *usually right on new cases from the same source*. Making
"usually" and "same source" precise is much of what this book is about.

### Samuel's checkers player

The phrase "machine learning" goes back at least to Arthur Samuel, an engineer at IBM, who wrote programs to play
checkers (draughts) on IBM's early computers. His paper "Some Studies in Machine Learning Using the Game of
Checkers" appeared in the *IBM Journal of Research and Development* in 1959. It is worth knowing what the program
actually did, because two of its ideas are still central.

A checkers program looks ahead a few moves and must judge the positions it reaches: is this position good for me?
Samuel's program scored a position with a weighted sum of features he chose by hand, such as the difference in the
number of pieces, the number of kings, and measures of mobility and control of the centre. The *weights*, the numbers
saying how much each feature counts, were not fixed by Samuel. The program adjusted them itself, by playing games,
including games against a copy of itself, and nudging the weights so that its quick judgement of a position agreed
better with what its deeper look-ahead found. That is learning in a modern sense: a fixed form of rule (a weighted
sum of features) with adjustable numbers (the weights), tuned by experience to do better at a task. Samuel also used
"rote learning", storing positions it had already analysed so that it did not have to analyse them again. In the
paper he reported that the program learned to play a better game than he, its author, could.

Two ideas from Samuel are with us in every later chapter. First, a model is usually a fixed shape with adjustable
numbers called **parameters**, and learning means choosing the parameters. Second, the program needs a signal that
says whether a change made things better or worse.

### Mitchell's definition

Tom Mitchell, in his textbook *Machine Learning* (1997), gave the definition that most courses still start from:

> A computer program is said to learn from experience E with respect to some class of tasks T and performance
> measure P, if its performance at tasks in T, as measured by P, improves with experience E.

The definition has three parts, and naming them is the first step of every project.

- The **task** $T$ is what the program does: tell lemons from oranges, predict tomorrow's temperature, play checkers.
- The **experience** $E$ is what it learns from: a table of measured fruit, years of weather records, games played.
- The **performance measure** $P$ is how we score it: the fraction of fruit labelled correctly, the average size of
  the temperature error, the fraction of games won.

For Samuel's program, $T$ is playing checkers, $E$ is games played (many against itself) and $P$ is the fraction of
games won against some fixed opponents. For a spam filter, $T$ is sorting incoming email into spam and not spam, $E$
is a collection of emails people have marked, and $P$ might be the fraction sorted correctly, or something more
careful, since losing a real email is worse than letting one spam through. (Chapter 7 is about choosing $P$ well.)

Notice what the definition does not say. It does not say the program understands fruit, or that it must work the way
people learn. It is a definition by behaviour: performance improves with experience. It also makes clear that
learning is always learning *something*, measured *somehow*. A program that "learns" without a stated task and
measure has not been defined at all.

### Why now, and why at all

Why use learning instead of rules? Four reasons come up again and again.

1. **Nobody can write the rules.** We recognise faces and voices without being able to say how.
2. **The rules change.** Spammers change their messages every week; a learned filter can be retrained on new mail.
3. **The rules are different for everyone.** Which films you will enjoy is not the same rule as for your neighbour.
4. **There is more data than anyone can read.** A learner can find patterns in millions of records.

There is also a fifth, practical reason that matters for space exploration. A signal between Earth and Mars takes
between about 3 and 22 minutes each way, so a rover cannot wait for people on Earth to judge every image. Curiosity's
AEGIS software picks rock targets for its laser spectrometer by itself, from features it computes in its own camera
images, and Perseverance's AutoNav judges from its own images where it is safe to drive. These systems are a mix of
hand-designed rules and tuned numbers, and they are a good reminder that "learned" and "hand-written" are two ends of
a range, not two separate worlds.

## 1.2 Kinds of learning

What exactly does the learner get to see? The answer splits machine learning into a few big families. The words in
this section are used in every later chapter, so it is worth getting them straight.

Some vocabulary first. One example is a **data point** or **instance**, for instance one fruit. The measured
quantities that describe it, such as length and width, are its **features**; we collect them in a list of numbers
$x$, called the **feature vector**. If the example comes with a right answer, that answer is its **label** or
**target**, written $y$. A collection of examples is a **dataset**.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 330" role="img" aria-label="Four panels. Supervised: points with labels and a fitted line through them. Unsupervised: unlabelled points forming two groups, circled. Self-supervised: the sentence the rover drove across the blank, with the blank filled by the model as the word crater. Reinforcement: an agent box and an environment box joined by arrows labelled action, and reward and new state.">
  <rect x="10" y="10" width="305" height="150" rx="8" fill="none" stroke="currentColor" stroke-opacity="0.5"/>
  <text x="22" y="32" font-size="14" font-weight="bold" fill="currentColor">supervised</text>
  <text x="22" y="50" font-size="12" fill="currentColor">inputs with answers: learn x to y</text>
  <line x1="40" y1="145" x2="290" y2="145" stroke="currentColor"/>
  <line x1="40" y1="145" x2="40" y2="60" stroke="currentColor"/>
  <line x1="50" y1="138" x2="280" y2="70" stroke="#eea66f" stroke-width="2.5"/>
  <circle cx="70" cy="128" r="4.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="100" cy="126" r="4.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="130" cy="108" r="4.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="160" cy="108" r="4.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="190" cy="92" r="4.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="220" cy="94" r="4.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="250" cy="74" r="4.5" fill="#9cc9ea" stroke="currentColor"/>
  <rect x="325" y="10" width="305" height="150" rx="8" fill="none" stroke="currentColor" stroke-opacity="0.5"/>
  <text x="337" y="32" font-size="14" font-weight="bold" fill="currentColor">unsupervised</text>
  <text x="337" y="50" font-size="12" fill="currentColor">inputs only: find structure</text>
  <ellipse cx="410" cy="105" rx="42" ry="30" fill="#7ccf9a" fill-opacity="0.2" stroke="currentColor" stroke-dasharray="4 3"/>
  <ellipse cx="545" cy="110" rx="45" ry="32" fill="#eea66f" fill-opacity="0.2" stroke="currentColor" stroke-dasharray="4 3"/>
  <circle cx="395" cy="95" r="4" fill="currentColor"/>
  <circle cx="415" cy="112" r="4" fill="currentColor"/>
  <circle cx="425" cy="92" r="4" fill="currentColor"/>
  <circle cx="400" cy="118" r="4" fill="currentColor"/>
  <circle cx="430" cy="115" r="4" fill="currentColor"/>
  <circle cx="530" cy="100" r="4" fill="currentColor"/>
  <circle cx="555" cy="118" r="4" fill="currentColor"/>
  <circle cx="565" cy="98" r="4" fill="currentColor"/>
  <circle cx="540" cy="125" r="4" fill="currentColor"/>
  <circle cx="520" cy="115" r="4" fill="currentColor"/>
  <rect x="10" y="170" width="305" height="150" rx="8" fill="none" stroke="currentColor" stroke-opacity="0.5"/>
  <text x="22" y="192" font-size="14" font-weight="bold" fill="currentColor">self-supervised</text>
  <text x="22" y="210" font-size="12" fill="currentColor">hide part of the input, predict it</text>
  <text x="30" y="250" font-size="14" fill="currentColor">the rover drove across the</text>
  <rect x="210" y="234" width="66" height="22" fill="#9cc9ea" fill-opacity="0.4" stroke="currentColor"/>
  <text x="243" y="250" font-size="14" text-anchor="middle" fill="currentColor">?</text>
  <line x1="243" y1="260" x2="243" y2="280" stroke="currentColor"/>
  <polygon points="243,288 238,278 248,278" fill="currentColor"/>
  <text x="243" y="306" font-size="14" text-anchor="middle" fill="currentColor">crater</text>
  <rect x="325" y="170" width="305" height="150" rx="8" fill="none" stroke="currentColor" stroke-opacity="0.5"/>
  <text x="337" y="192" font-size="14" font-weight="bold" fill="currentColor">reinforcement</text>
  <text x="337" y="210" font-size="12" fill="currentColor">act, get rewards, improve the actions</text>
  <rect x="345" y="235" width="100" height="40" rx="6" fill="#eea66f" fill-opacity="0.35" stroke="currentColor"/>
  <text x="395" y="260" font-size="13" text-anchor="middle" fill="currentColor">agent</text>
  <rect x="505" y="235" width="110" height="40" rx="6" fill="#7ccf9a" fill-opacity="0.35" stroke="currentColor"/>
  <text x="560" y="260" font-size="13" text-anchor="middle" fill="currentColor">environment</text>
  <path d="M 420 235 Q 475 215 530 233" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <polygon points="536,236 525,236 530,228" fill="currentColor"/>
  <text x="475" y="220" font-size="12" text-anchor="middle" fill="currentColor">action</text>
  <path d="M 540 275 Q 475 300 420 278" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <polygon points="414,275 425,275 420,283" fill="currentColor"/>
  <text x="475" y="308" font-size="12" text-anchor="middle" fill="currentColor">reward, new state</text>
</svg>
<figcaption>The four big families. They differ in what the learner is given: answers (supervised), nothing but
inputs (unsupervised), answers made from the input itself (self-supervised), or rewards for its own actions
(reinforcement).</figcaption>
</figure>

### Supervised learning

In **supervised learning** every training example comes with its label: pairs $(x_1,y_1),\dots,(x_n,y_n)$. The goal
is a function $f$ such that $f(x)$ is close to the true $y$ for new $x$. It is called supervised because someone, the
"supervisor", has provided the right answers. Two kinds are distinguished by what $y$ is.

- In **regression**, $y$ is a number on a continuous scale: the price of a house, tomorrow's temperature, the
  distance a rover can drive on one battery charge. "Close" means a small numerical error. Chapter 4 is the first
  regression model.
- In **classification**, $y$ is one of a fixed set of **classes** or categories: lemon or orange, spam or not spam,
  which of ten digits is in an image. "Close" means the same class. With two classes we speak of **binary**
  classification; with more, **multiclass**. Chapter 6 is the first classification model built on numbers, but the
  learner in section 1.3 is already a classifier.

The same data can serve both. From weather records you can predict tomorrow's rainfall in millimetres (regression) or
just "rain or no rain" (classification). Which you choose depends on the question.

### Unsupervised learning

In **unsupervised learning** there are no labels, only inputs $x_1,\dots,x_n$. The goal is to find structure in
them. Common tasks:

- **Clustering**: group similar points together, for example customers with similar buying habits (Chapter 13).
- **Dimensionality reduction**: describe each point with fewer numbers while keeping what matters, for example to
  draw a picture of high-dimensional data on a page (Chapter 14).
- **Density estimation**: learn how probable each kind of input is, so that unusual ones can be flagged.

Unsupervised learning is harder to score, because there is no right answer to compare with. Is a grouping of
customers into three clusters better than into five? That depends on what you will use the groups for.

### Self-supervised learning

**Self-supervised learning** is a clever middle way. The data has no labels written by people, but we make labels
from the data itself, by hiding part of each input and asking the model to predict it. Hide the next word of a
sentence and predict it from the words before. Hide a patch of an image and predict it from the rest. Technically
this is supervised learning, since there are inputs and targets, but the targets cost nothing, so the amount of
training data can be enormous: all the text and images anyone can collect. The language models of Chapter 19 are
trained this way, by predicting the next token; a model that has learned to do that well has, as a side effect,
learned a great deal about language that can then be used for other tasks.

### Reinforcement learning

In **reinforcement learning** there are no examples of right answers at all. An **agent** takes **actions** in an
**environment**. After each action it sees the new **state** of the environment and receives a number called a
**reward**. The goal is to learn a way of choosing actions, a **policy**, that collects as much reward as possible
over time. Samuel's checkers program was an early example: the "reward" is winning, and it arrives only at the end of
a game, so the program must work out which of its many moves deserve the credit. Reinforcement learning is the subject
of a later book on this site, Artificial intelligence; this book touches it only in passing.

### Other words you will meet

A few other terms describe *how* the data arrives rather than what it contains. In **batch** (or offline) learning,
the whole dataset is available at once. In **online** learning, examples arrive one at a time and the model updates
after each. **Semi-supervised** learning uses a few labelled examples together with many unlabelled ones. **Active**
learning lets the learner choose which examples to ask a person to label. These are variations on the four families,
not new families.

## 1.3 A first learner from scratch

What is the simplest learner that could possibly work? Here is a candidate: to label a new fruit, find the fruit in
the table that is most like it and copy its label. "Most like" needs a measure, and the simplest one is the
straight-line distance between the feature vectors. This is the **nearest-neighbour classifier**, and despite its
simplicity it is a real learner that is still used, often as a baseline that cleverer methods must beat.

Here is our experience $E$: ten fruit, measured by hand. Each has two features, the length and the width in
centimetres, and a label.

| fruit | length (cm) | width (cm) | label |
|---|---|---|---|
| 1 | 7.0 | 7.2 | orange |
| 2 | 7.6 | 7.5 | orange |
| 3 | 6.8 | 6.9 | orange |
| 4 | 8.0 | 7.8 | orange |
| 5 | 7.2 | 7.4 | orange |
| 6 | 8.5 | 5.9 | lemon |
| 7 | 9.2 | 6.3 | lemon |
| 8 | 8.0 | 5.6 | lemon |
| 9 | 9.6 | 6.6 | lemon |
| 10 | 8.8 | 6.1 | lemon |

Each fruit is a point in a plane: length along one axis, width along the other. The **distance** between two points
$p=(p_1,p_2)$ and $q=(q_1,q_2)$ is given by Pythagoras' theorem:

$$
d(p,q)=\sqrt{(p_1-q_1)^2+(p_2-q_2)^2}.
$$

With more features, say $m$ of them, the same formula simply has $m$ squared differences under the root. This is the
**Euclidean distance**; Chapter 3 calls it the norm of $p-q$.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 390" role="img" aria-label="Scatter plot of the ten fruit, length from 6.5 to 10 centimetres across and width from 5.4 to 8 down. Five oranges, drawn as orange circles, sit up and to the left, where width is close to length. Five lemons, drawn as blue squares, sit down and to the right, longer than wide. A new fruit at length 8.1, width 6.4 is marked with a cross; a dashed circle around it reaches its three nearest neighbours, all lemons.">
  <line x1="60" y1="340" x2="480" y2="340" stroke="currentColor" stroke-width="1.5"/>
  <line x1="60" y1="340" x2="60" y2="28" stroke="currentColor" stroke-width="1.5"/>
  <line x1="120" y1="340" x2="120" y2="346" stroke="currentColor"/>
  <text x="120" y="362" font-size="12" text-anchor="middle" fill="currentColor">7</text>
  <line x1="240" y1="340" x2="240" y2="346" stroke="currentColor"/>
  <text x="240" y="362" font-size="12" text-anchor="middle" fill="currentColor">8</text>
  <line x1="360" y1="340" x2="360" y2="346" stroke="currentColor"/>
  <text x="360" y="362" font-size="12" text-anchor="middle" fill="currentColor">9</text>
  <line x1="480" y1="340" x2="480" y2="346" stroke="currentColor"/>
  <text x="480" y="362" font-size="12" text-anchor="middle" fill="currentColor">10</text>
  <line x1="54" y1="268" x2="60" y2="268" stroke="currentColor"/>
  <text x="48" y="272" font-size="12" text-anchor="end" fill="currentColor">6</text>
  <line x1="54" y1="148" x2="60" y2="148" stroke="currentColor"/>
  <text x="48" y="152" font-size="12" text-anchor="end" fill="currentColor">7</text>
  <line x1="54" y1="28" x2="60" y2="28" stroke="currentColor"/>
  <text x="48" y="32" font-size="12" text-anchor="end" fill="currentColor">8</text>
  <text x="270" y="380" font-size="13" text-anchor="middle" fill="currentColor">length (cm)</text>
  <text x="16" y="190" font-size="13" text-anchor="middle" fill="currentColor" transform="rotate(-90 16 190)">width (cm)</text>
  <circle cx="252.0" cy="220.0" r="96.7" fill="#7ccf9a" fill-opacity="0.15" stroke="currentColor" stroke-dasharray="5 4"/>
  <circle cx="120.0" cy="124.0" r="7" fill="#eea66f" stroke="currentColor"/>
  <circle cx="192.0" cy="88.0" r="7" fill="#eea66f" stroke="currentColor"/>
  <circle cx="96.0" cy="160.0" r="7" fill="#eea66f" stroke="currentColor"/>
  <circle cx="240.0" cy="52.0" r="7" fill="#eea66f" stroke="currentColor"/>
  <circle cx="144.0" cy="100.0" r="7" fill="#eea66f" stroke="currentColor"/>
  <rect x="293.5" y="273.5" width="13" height="13" fill="#9cc9ea" stroke="currentColor"/>
  <rect x="377.5" y="225.5" width="13" height="13" fill="#9cc9ea" stroke="currentColor"/>
  <rect x="233.5" y="309.5" width="13" height="13" fill="#9cc9ea" stroke="currentColor"/>
  <rect x="425.5" y="189.5" width="13" height="13" fill="#9cc9ea" stroke="currentColor"/>
  <rect x="329.5" y="249.5" width="13" height="13" fill="#9cc9ea" stroke="currentColor"/>
  <path d="M 244.0 220.0 L 260.0 220.0 M 252.0 212.0 L 252.0 228.0" stroke="currentColor" stroke-width="2.5"/>
  <text x="264.0" y="210.0" font-size="12" fill="currentColor">new (8.1, 6.4)</text>
  <circle cx="505" cy="60" r="7" fill="#eea66f" stroke="currentColor"/>
  <text x="519" y="64" font-size="13" fill="currentColor">orange</text>
  <rect x="498.5" y="83.5" width="13" height="13" fill="#9cc9ea" stroke="currentColor"/>
  <text x="519" y="94" font-size="13" fill="currentColor">lemon</text>
  <path d="M 497 120 L 513 120 M 505 112 L 505 128" stroke="currentColor" stroke-width="2.5"/>
  <text x="519" y="124" font-size="13" fill="currentColor">new fruit</text>
  <line x1="495" y1="150" x2="513" y2="150" stroke="currentColor" stroke-dasharray="5 4"/>
  <text x="519" y="148" font-size="13" fill="currentColor">3 nearest</text>
  <text x="519" y="164" font-size="13" fill="currentColor">neighbours</text>
</svg>
<figcaption>The ten fruit as points. Oranges (circles) are about as wide as they are long; lemons (squares) are
longer than wide. The dashed circle around the new fruit passes through its third-nearest neighbour; the three
fruit inside or on it are all lemons.</figcaption>
</figure>

### Tracing it by hand

A new fruit arrives with length 8.1 cm and width 6.4 cm. Which is it? Compute its distance to every fruit in the
table. For fruit 6, the lemon at (8.5, 5.9):

$$
d=\sqrt{(8.5-8.1)^2+(5.9-6.4)^2}=\sqrt{0.16+0.25}=\sqrt{0.41}\approx0.640.
$$

For fruit 2, the orange at (7.6, 7.5): $\sqrt{0.25+1.21}=\sqrt{1.46}\approx1.208$. Doing all ten and sorting from
nearest to farthest gives the table below (the program prints exactly these numbers).

| rank | fruit | features | label | distance |
|---|---|---|---|---|
| 1 | 6 | (8.5, 5.9) | lemon | 0.640 |
| 2 | 10 | (8.8, 6.1) | lemon | 0.762 |
| 3 | 8 | (8.0, 5.6) | lemon | 0.806 |
| 4 | 7 | (9.2, 6.3) | lemon | 1.105 |
| 5 | 2 | (7.6, 7.5) | orange | 1.208 |
| 6 | 5 | (7.2, 7.4) | orange | 1.345 |
| 7 | 1 | (7.0, 7.2) | orange | 1.360 |
| 8 | 3 | (6.8, 6.9) | orange | 1.393 |
| 9 | 4 | (8.0, 7.8) | orange | 1.404 |
| 10 | 9 | (9.6, 6.6) | lemon | 1.513 |

The nearest fruit is a lemon, so the **1-nearest-neighbour** classifier says "lemon". A single neighbour can be
misleading if it happens to be an odd fruit, so a common improvement is to let the $k$ nearest neighbours vote: the
**$k$-nearest-neighbour** classifier, or $k$-NN. With $k=3$ the three nearest are all lemons; with $k=5$ the vote is
four lemons to one orange. Every choice says "lemon". Notice the last row: lemon 9 is the *farthest* fruit of all,
because it is unusually long. Distance measures similarity in features, not membership of a class.

### The code

Here is the whole learner. The function `distance` is the formula above. The function `knn_predict` sorts the table
by distance to the new point, keeps the first $k$ rows, and returns the most common label among them.

```python
--8<-- "books/machine-learning/ch01_first_learner.py"
```

Output:

```
distances from the new fruit (8.1, 6.4)
  (8.5, 5.9)   lemon   0.640
  (8.8, 6.1)   lemon   0.762
  (8.0, 5.6)   lemon   0.806
  (9.2, 6.3)   lemon   1.105
  (7.6, 7.5)   orange  1.208
  (7.2, 7.4)   orange  1.345
  (7.0, 7.2)   orange  1.360
  (6.8, 6.9)   orange  1.393
  (8.0, 7.8)   orange  1.404
  (9.6, 6.6)   lemon   1.513
k = 1: predicted lemon
k = 3: predicted lemon
k = 5: predicted lemon

new fruit (7.4, 7.0): 1-NN says orange, 3-NN says orange
new fruit (9.0, 6.0): 1-NN says lemon, 3-NN says lemon
new fruit (7.9, 6.9): 1-NN says orange, 3-NN says orange
leave-one-out, k = 1: 10 of 10 right
leave-one-out, k = 3: 10 of 10 right
```

Where is the "learning"? The training step of $k$-NN is just storing the table. All the work happens when a question
is asked. Learners like this are called **lazy** or **instance-based**; most later learners are **eager**, doing their
work up front to produce a compact model (a few numbers) and then answering questions quickly. Lazy or eager, the
behaviour fits Mitchell's definition: give $k$-NN more measured fruit and, as a rule, its predictions on new fruit
become more accurate.

The last two lines of the output use a trick we will meet properly in Chapter 7. To check the learner honestly, we
hide one fruit, predict it from the other nine, and repeat for each fruit in turn. That is called **leave-one-out**
evaluation. Here every fruit is predicted correctly, which says the two classes are well separated in this tiny
table, not that the learner is perfect.

### What the nearest-neighbour rule assumes

Every learner makes assumptions, stated or not. Nearest neighbour assumes that **points that are close in feature
space tend to have the same label**. For fruit measured by length and width, that is plausible. Three things can
break it, and each gets a later chapter.

1. **The units of the features.** If we measured length in millimetres and width in metres, the length differences
   would be thousands of times bigger and would decide every distance on their own. Chapter 2 explains scaling.
2. **Irrelevant features.** Add a feature "day of the week the fruit was bought", and distances fill up with noise.
3. **Many features.** In hundreds of dimensions, almost all points are nearly the same distance from each other, and
   "nearest" stops meaning much. Chapter 9 shows this "curse of dimensionality" by computation.

The cost is also worth a glance. Predicting one point means computing $n$ distances, each with $m$ features, and
sorting them: about $nm+n\log n$ steps (only selecting the $k$ smallest, as in
[Chapter 6 of the Algorithms book](../algorithms/06-Sorting-in-Linear-Time-and-Selection.md), brings it down to
about $nm$). For millions of points that is slow, which is why Chapter 9 looks at faster search.

<figure class="play" data-play="fruitnn"><span class="ai-tag">AI-created</span><figcaption>Try it: tap to place a new fruit among the ten in the table above; the nearest one gives it its label.</figcaption></figure>

## 1.4 Training, validation and test data

How do we know whether a learner is any good? The obvious answer, "see how often it is right on the examples we
have", is wrong in an instructive way.

Try it on the 1-nearest-neighbour classifier. Ask it to label a fruit from its own table. The nearest fruit to fruit
6 is fruit 6 itself, at distance 0, so it copies fruit 6's label and is right. That happens for every fruit: on its own
training data, 1-NN is always 100% right (unless two identical points carry different labels). That score tells us
nothing about new fruit. A student who memorises last year's exam answers scores full marks on last year's exam and
may know nothing.

The fix is to keep some data back. The learner never sees it during training; we use it only to measure. The idea is
so central that the pieces have standard names.

- The **training set** is the data the learner fits its model to.
- The **validation set** (sometimes called the development set) is held back from training and used to make
  *choices*: which learner, which value of $k$, which features. Each choice is a small act of learning from the
  validation set.
- The **test set** is held back from everything and used *once*, at the very end, to estimate how well the final
  model will do on new data.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 200" role="img" aria-label="A bar representing 300 examples, split into training 180 examples, validation 60 and test 60. Below the training part: fit the model. Below validation: choose k, features, learner. Below test: estimate once, at the end. An arrow from validation back to training is labelled try again.">
  <rect x="20" y="40" width="360" height="46" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1.5"/>
  <rect x="380" y="40" width="120" height="46" fill="#7ccf9a" fill-opacity="0.45" stroke="currentColor" stroke-width="1.5"/>
  <rect x="500" y="40" width="120" height="46" fill="#eea66f" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
  <text x="200" y="68" font-size="14" text-anchor="middle" fill="currentColor">training: 180 examples (60%)</text>
  <text x="440" y="68" font-size="14" text-anchor="middle" fill="currentColor">validation: 60</text>
  <text x="560" y="68" font-size="14" text-anchor="middle" fill="currentColor">test: 60</text>
  <text x="200" y="112" font-size="13" text-anchor="middle" fill="currentColor">fit the model's parameters</text>
  <text x="440" y="112" font-size="13" text-anchor="middle" fill="currentColor">choose k, features,</text>
  <text x="440" y="130" font-size="13" text-anchor="middle" fill="currentColor">learner</text>
  <text x="560" y="112" font-size="13" text-anchor="middle" fill="currentColor">estimate once,</text>
  <text x="560" y="130" font-size="13" text-anchor="middle" fill="currentColor">at the end</text>
  <path d="M 440 140 Q 330 190 210 128" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <polygon points="204,124 216,126 210,134" fill="currentColor"/>
  <text x="330" y="186" font-size="12" text-anchor="middle" fill="currentColor">try again with another choice</text>
  <text x="20" y="28" font-size="13" fill="currentColor">all 300 labelled examples, shuffled</text>
</svg>
<figcaption>The usual three-way split. The training set fits; the validation set chooses; the test set is touched
once, after every choice has been made, so that its score is an honest estimate for new data.</figcaption>
</figure>

### An experiment

The program below makes 300 synthetic points in two overlapping clouds: class 0 is scattered around $(0,0)$ and
class 1 around $(1.5,1.5)$, each with the bell-shaped spread of the normal distribution (Chapter 3 explains it). The
clouds overlap, so no learner can be perfect. In fact, because we built the data ourselves, we can work out the best
possible accuracy: the best rule labels a point by which centre it is nearer, and it is right about 85.6% of the
time (Chapter 12 derives this; the calculation uses the normal distribution's tail). The data is shuffled and split
180 / 60 / 60. We try several values of $k$, choose the best on validation, and only then look at the test set.

```python
--8<-- "books/machine-learning/ch01_holdout.py"
```

Output:

```
train 180, validation 60, test 60
   k   train acc   val acc
   1       1.000     0.850
   3       0.883     0.833
   5       0.867     0.800
   9       0.850     0.883
  15       0.861     0.933
  25       0.856     0.900
  51       0.850     0.900
chosen k = 15; test accuracy = 0.850
over 200 repeats: mean best validation acc = 0.866, mean test acc of that k = 0.839
```

Read the table row by row.

- With $k=1$ the training accuracy is a perfect 1.000, exactly as argued above, and it means nothing.
- The validation accuracy jumps around: 0.850, 0.833, 0.800, 0.883, 0.933. With only 60 validation points, one
  point is worth $1/60\approx0.017$, so these differences are a few points each way, partly luck.
- The best validation score, 0.933 at $k=15$, is *higher than the best possible accuracy* of about 0.856. That is a
  sure sign of luck: on this particular set of 60 points, $k=15$ happened to be right a few extra times.
- The test accuracy of the chosen model, 0.850, is close to the best possible, and it is the honest number.

### Why the chosen score is too optimistic

The last line of the output repeats the whole experiment 200 times with fresh data. On average the best validation
score is 0.866, but the test score of the same choice is 0.839. The best of several noisy scores is biased upward.

Here is the reason in one paragraph. Each validation score is the true accuracy plus some random error, which is as
likely to be positive as negative. When we pick the *largest* of seven scores, we tend to pick one whose error was
positive. So the winner's score overstates its true accuracy, even though no single score is biased. This is the
same effect that makes the luckiest of many fund managers look like a genius. The more choices we try on one
validation set, the bigger the effect, which is why the validation set cannot double as the test set. The test set
is useful exactly because we never chose anything with it.

Three practical rules follow.

1. **Hold out the test set first**, before you look at the data closely, and do not touch it until the end.
2. **Report the test score of one model**, chosen in advance by the validation set. If you look at test scores and go
   back to change the model, the test set has become a second validation set, and you need a new test set.
3. **Make the held-out sets resemble the future.** Held-out data estimates performance only on data like itself.
   Chapter 2 (section 2.6) shows how a careless split, for example one that puts the same patient in both training
   and test sets, gives scores that collapse in use.

How big should each part be? There is no single answer. A larger test set gives a more precise estimate (Chapter 7
computes how precise), but leaves less to train on. With small datasets, **cross-validation** (Chapter 7) reuses each
point for both training and validation in turn, as our leave-one-out check did.

### Generalisation

The word for doing well on new data is **generalisation**. The difference between the score on training data and
the score on new data is the **generalisation gap**. A model with a large gap has learned details of its training set
that do not carry over, called **overfitting**; a model that does badly even on training data is **underfitting**.
In the table, $k=1$ overfits (perfect on training, worse on validation) and $k=51$ is starting to smooth so much that
it loses detail. Chapter 8 studies this trade-off in depth, and Chapter 21 asks the deep question of *why* a model
fitted to some data should work on other data at all.

## 1.5 The workflow

What does a real machine-learning project look like from start to finish? The details vary, but the steps are
nearly always the same, and most failures come from skipping one.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 170" role="img" aria-label="Seven boxes in a row joined by arrows: question, data, model, loss, fit, evaluate, deploy. A curved arrow from evaluate back to data is labelled often: go back.">
  <rect x="10" y="50" width="76" height="40" rx="6" fill="#eea66f" fill-opacity="0.35" stroke="currentColor"/>
  <text x="48" y="75" font-size="13" text-anchor="middle" fill="currentColor">question</text>
  <rect x="100" y="50" width="76" height="40" rx="6" fill="#9cc9ea" fill-opacity="0.4" stroke="currentColor"/>
  <text x="138" y="75" font-size="13" text-anchor="middle" fill="currentColor">data</text>
  <rect x="190" y="50" width="76" height="40" rx="6" fill="#9cc9ea" fill-opacity="0.4" stroke="currentColor"/>
  <text x="228" y="75" font-size="13" text-anchor="middle" fill="currentColor">model</text>
  <rect x="280" y="50" width="76" height="40" rx="6" fill="#9cc9ea" fill-opacity="0.4" stroke="currentColor"/>
  <text x="318" y="75" font-size="13" text-anchor="middle" fill="currentColor">loss</text>
  <rect x="370" y="50" width="76" height="40" rx="6" fill="#9cc9ea" fill-opacity="0.4" stroke="currentColor"/>
  <text x="408" y="75" font-size="13" text-anchor="middle" fill="currentColor">fit</text>
  <rect x="460" y="50" width="76" height="40" rx="6" fill="#7ccf9a" fill-opacity="0.4" stroke="currentColor"/>
  <text x="498" y="75" font-size="13" text-anchor="middle" fill="currentColor">evaluate</text>
  <rect x="550" y="50" width="80" height="40" rx="6" fill="#eea66f" fill-opacity="0.35" stroke="currentColor"/>
  <text x="590" y="75" font-size="13" text-anchor="middle" fill="currentColor">deploy</text>
  <line x1="86" y1="70" x2="94" y2="70" stroke="currentColor"/>
  <polygon points="100,70 93,66 93,74" fill="currentColor"/>
  <line x1="176" y1="70" x2="184" y2="70" stroke="currentColor"/>
  <polygon points="190,70 183,66 183,74" fill="currentColor"/>
  <line x1="266" y1="70" x2="274" y2="70" stroke="currentColor"/>
  <polygon points="280,70 273,66 273,74" fill="currentColor"/>
  <line x1="356" y1="70" x2="364" y2="70" stroke="currentColor"/>
  <polygon points="370,70 363,66 363,74" fill="currentColor"/>
  <line x1="446" y1="70" x2="454" y2="70" stroke="currentColor"/>
  <polygon points="460,70 453,66 453,74" fill="currentColor"/>
  <line x1="536" y1="70" x2="544" y2="70" stroke="currentColor"/>
  <polygon points="550,70 543,66 543,74" fill="currentColor"/>
  <path d="M 498 92 Q 320 160 142 98" fill="none" stroke="currentColor" stroke-width="1.5" stroke-dasharray="5 4"/>
  <polygon points="138,93 149,96 142,104" fill="currentColor"/>
  <text x="320" y="150" font-size="12" text-anchor="middle" fill="currentColor">often: go back and fix the data or the model</text>
  <text x="320" y="30" font-size="12" text-anchor="middle" fill="currentColor">and after deployment: watch it, because the world changes</text>
</svg>
<figcaption>The workflow. The arrows go forward, but real projects loop back many times, most often from
evaluation to the data.</figcaption>
</figure>

**1. The question.** State the task $T$ and the performance measure $P$ in plain words, and say what decision the
predictions will feed. "Predict which rock targets in an image are worth a closer look, and count it a success if the
chosen targets are the ones a geologist would choose" is a question. "Do some AI on the rover images" is not. Also
ask: would a simple rule do? If a threshold on one measurement solves the problem, you do not need a learner.

**2. The data.** Find or collect examples, decide what the features and labels are, clean them, and split off the
test set. In practice this step takes most of the time, and it is where most mistakes live. Chapter 2 is about it.

**3. The model.** Choose a family of possible rules, called the **hypothesis class**: all straight lines, all
decision trees of depth five, all neural networks of a certain shape. The learner will pick one member of the family.
The choice encodes assumptions about the problem; a family of straight lines cannot represent a curve, however much
data it sees.

**4. The loss.** Choose a **loss function**: a number that measures how badly the model does on one example, such as
the squared difference between prediction and truth. The learner will try to make the average loss on the training
data small. The loss is not always the same as the performance measure $P$. Accuracy, for example, jumps in steps
and gives no hint of which direction is better, so we often train with a smooth stand-in for it (Chapter 6).

**5. The fit.** Run the learning algorithm: find the member of the family with the smallest training loss, perhaps
with a penalty for complexity. This is an optimisation problem. Sometimes it has an exact solution (Chapter 4);
usually it is solved step by step by gradient descent (Chapters 4 and 5).

**6. Evaluate.** Measure performance on validation data, look at the mistakes one by one, compare with a simple
baseline (always predicting the most common class, or $k$-NN), and loop back. When all choices are final, measure
once on the test set.

**7. Deploy.** Put the model to work. Then keep watching it, because the world drifts away from the training data:
customers change, sensors age, spammers adapt. Chapter 22 covers this.

Steps 3, 4 and 5 together are what "fitting a model" means, and they are a pattern you will see in almost every
chapter: **a family of models, a loss, and an optimiser**. Linear regression in Chapter 4 is: straight lines, squared
error, solve exactly. Logistic regression in Chapter 6 is: linear scores passed through a sigmoid, cross-entropy,
gradient descent. A deep network in Chapter 15 is: a stack of layers, cross-entropy, gradient descent with
backpropagation. When you meet a new method, look for these three parts first.

A baseline deserves one more sentence. A model that is 95% accurate sounds good until you learn that 95% of the
examples belong to one class, so the rule "always say that class" also scores 95%. Always compute the simplest
baseline first; it tells you what "good" means for this data.

## 1.6 What machine learning cannot do

What are the limits? There are some hard ones, and knowing them saves a great deal of wasted effort. Here are three.

### No data, no learning

A learner can only find patterns that are in its data. If the data does not contain the information needed to
predict the label, no learner can predict it. If a spam filter sees only the length of each email, it cannot learn
which words matter. If a fruit classifier has never seen a lime, it will call every lime a lemon or an orange,
because those are the only answers it knows.

A subtler form of the same limit: the data must cover the situations the model will face. A model trained on
images taken in daylight may fail at dusk. A rover's hazard detector trained only on sandy terrain has no basis for
judging a field of boulders. Learning generalises *between* the examples it has seen far better than *beyond* them.
Going beyond the range of the training data is called **extrapolation**, and it is where models fail most
dramatically.

### Correlation is not cause

Learners find **correlations**: patterns where two things tend to go together. They do not, by themselves, find
**causes**: what would happen if we *changed* one thing. The classic example is that ice cream sales and drowning
deaths rise and fall together over a year. A model can predict drownings from ice cream sales quite well. But banning
ice cream would not save anyone, because both are caused by a third thing, hot weather, which sends people to buy ice
cream and to swim. A hidden cause like the weather is called a **confounder**.

This matters whenever a prediction is used to make a decision. Suppose a model trained on hospital records learns
that patients with asthma are *less* likely to die of pneumonia. A real study of this kind found exactly that pattern
in its data (Caruana et al. 2015 describe it), and the reason was that asthma patients with pneumonia were treated more intensively, so they did
better. A model that used the pattern to send asthma patients home would be badly wrong. The pattern was real; the
causal reading of it was not.

Prediction is fine for prediction: if you only want to forecast drownings to plan lifeguard rotas, ice cream sales
are a perfectly useful feature. The mistake is to read a predictive pattern as an answer to "what if we change it".
Answering that question needs either an experiment (change the thing and see) or extra assumptions about how the
data was generated; the study of this is called **causal inference**, and Chapter 23 points to it as one of the big
open areas.

### The no-free-lunch theorem

*Level: intermediate.*

Is there a best learner, one that beats all others on every problem? The answer is no, and it can be proved. The
result is called the **no-free-lunch theorem**; the form below is due to David Wolpert (1996).

Here is the setting. There is a finite set of possible inputs. Some of them form the training set, and we are given
their true labels. The rest are **off-training-set** inputs: the learner has never seen them, and we score it only
on them, since that is what generalising means. The true labelling, the **target function**, is unknown.

**Theorem (no free lunch, finite form).** Let the inputs be a finite set, let the labels be 0 or 1, and fix a
training set of inputs. Average over all possible target functions, each counted once. Then every learner has the
same average accuracy on the off-training-set inputs, namely exactly $1/2$.

**Proof.** Take any learner, and any off-training-set input $x$. Group the target functions into pairs: two functions
are partners if they agree everywhere except at $x$, where one says 0 and the other says 1. Partners agree on the
training set, so they give the learner exactly the same training data, so the learner makes exactly the same
prediction at $x$ for both. That prediction is right for exactly one of the two partners. Every target function has
exactly one partner, so the pairs split all target functions into halves, and the learner is right at $x$ for
exactly half of all target functions. Average over the off-training-set inputs: the average accuracy is $1/2$, the
same for every learner. $\square$

The proof works for any learner, however clever, because the learner's prediction depends only on what it has seen,
and averaged over all targets, what it has seen says nothing about what it has not. The program checks this by brute
force. There are 8 inputs (the 3-bit strings), so $2^8=256$ target functions. Each learner sees the labels of 4
inputs and is scored on the other 4.

```python
--8<-- "books/machine-learning/ch01_no_free_lunch.py"
```

Output:

```
256 target functions, 4 unseen inputs each
learner             mean off-training accuracy  best  worst
nearest_neighbour                       0.5000  1.00   0.00
majority                                0.5000  1.00   0.00
always_zero                             0.5000  1.00   0.00
contrarian                              0.5000  1.00   0.00
parity_guess                            0.5000  1.00   0.00
on the parity target alone: {'nearest_neighbour': 0.0, 'majority': 0.5, 'always_zero': 0.5, 'contrarian': 1.0, 'parity_guess': 1.0}
```

Even the deliberately silly "contrarian", which always says the opposite of nearest neighbour, ties with nearest
neighbour on average. On any one target function they differ enormously: on the parity function (the label is 1 when
the number of 1 bits is odd), nearest neighbour gets every unseen input wrong and the contrarian gets every one right.

What does the theorem *mean*? It does not mean that learning is hopeless. It means that **a learner works only to the
extent that its assumptions match the world**. Averaged over all conceivable worlds, including the bizarre ones
where nearby points have unrelated labels, no assumption helps. But the real world is not an average over all
conceivable worlds. Fruit of similar shape usually are the same kind of fruit; tomorrow's weather resembles today's.
Every learner in this book has an **inductive bias**, a built-in preference for some answers over others (nearest
neighbour prefers "close means similar", linear regression prefers straight lines), and the art of machine learning
is choosing a bias that suits the problem. There is no free lunch: the assumptions have to come from somewhere,
usually from knowledge of the problem.

Shalev-Shwartz and Ben-David (2014, Chapter 5) prove a stronger, probabilistic version: for any learner there is a
distribution of data on which it fails badly while some other learner succeeds. Chapter 21 of this book returns to it.

## 1.7 A short honest history

How did we get from Samuel's checkers to programs that recognise images and write text? The history is often told as
legend. Here is a short version that sticks to what the sources say.

**Learning machines and the perceptron (1950s and 1960s).** Alongside Samuel's work, Frank Rosenblatt, a psychologist
at Cornell, proposed the **perceptron** in a 1958 paper in *Psychological Review*, "The Perceptron: A Probabilistic
Model for Information Storage and Organization in the Brain". A perceptron computes a weighted sum of its inputs and
outputs 1 if the sum passes a threshold, and it has a simple rule for adjusting its weights after each mistake.
Rosenblatt also built hardware versions. The learning rule comes with a guarantee: if a set of weights that classifies
every training example correctly exists, the rule finds one after a finite number of mistakes, a theorem proved by
Albert Novikoff in 1962. Chapter 6 builds the perceptron and proves that theorem.

**Limits and the first winter (late 1960s and 1970s).** In 1969 Marvin Minsky and Seymour Papert published
*Perceptrons*, a careful mathematical study of what single-layer perceptrons can and cannot compute. A single layer
cannot compute, for example, the XOR function (output 1 when exactly one of two inputs is 1). Networks with more
layers could, but nobody had a good way to train them. Interest and funding for this line of work fell. More broadly,
artificial-intelligence research in the 1970s promised more than it delivered, and funding was cut in several
countries; in Britain, the Lighthill report of 1973 was critical of the field. This period is called the first **AI
winter**. How much of the decline to blame on any one book or report is debated by historians, and you will see
the story told with more drama than the evidence supports.

**Backpropagation and the second wave (1980s).** In 1986 David Rumelhart, Geoffrey Hinton and Ronald Williams
published "Learning representations by back-propagating errors" in *Nature*, showing that networks with hidden layers
could be trained by **backpropagation**, an efficient way to compute how the error changes with every weight (Chapter
15 derives it). The method had been described earlier by others, including Paul Werbos in his 1974 thesis, but the
1986 paper made it widely known. Around the same time, "expert systems", built from hand-written rules, were a
commercial success, and their collapse in the late 1980s brought a second winter for AI as a whole.

**Statistical learning (1990s and 2000s).** The field grew closer to statistics. Support vector machines (Cortes and
Vapnik 1995; Chapter 10), boosting (Freund and Schapire; Chapter 11), random forests (Breiman 2001) and probabilistic
models (Chapter 12) came with theory about when they generalise, and worked well with modest computers. Neural networks
continued (LeCun and colleagues' convolutional networks read handwritten digits on bank cheques in the 1990s; Chapter
17), but were not the centre of attention.

**The 2012 ImageNet result.** ImageNet, a dataset of millions of labelled images built by Jia Deng, Fei-Fei Li and
colleagues (described in 2009), was the basis of a yearly competition, the ImageNet Large Scale Visual Recognition
Challenge, with 1000 classes and about 1.2 million training images. In 2012 Alex Krizhevsky, Ilya Sutskever and
Geoffrey Hinton entered a deep convolutional network trained on two graphics processors (GPUs). Their paper,
"ImageNet Classification with Deep Convolutional Neural Networks" (NeurIPS 2012), reports a top-5 test error of 15.3%,
against 26.2% for the second-best entry. (Top-5 error counts a prediction as wrong if the true class is not among the
model's five best guesses.) The gap was large, the method was a neural network trained by backpropagation, and the
result convinced much of the field that deep networks, given enough data and computing power, could beat
hand-engineered features. The years since have been dominated by deep learning, the subject of Part IV.

Three things changed between 1986 and 2012, and none of them was a single brilliant idea: far more labelled data,
far faster hardware (GPUs built for computer games turned out to be ideal for the matrix arithmetic of neural
networks), and many smaller improvements in how to train deep networks (Chapter 16). That is a useful lesson.
Progress in machine learning has come as much from data, computing power and careful engineering as from new
theory, and the theory, as Chapter 21 will show, still lags behind the practice in places.

## Check yourself

??? question "1. Name the task T, experience E and performance measure P for a program that predicts tomorrow's maximum temperature in a city."

    $T$: given today's weather measurements (and perhaps the previous days'), predict tomorrow's maximum
    temperature. $E$: a table of past days, each with its measurements and the maximum temperature on the following
    day. $P$: for example the average absolute difference, in degrees, between predicted and actual maximum on days
    not used for training. Smaller is better. This is supervised regression, because the label is a number.

??? question "2. Supervised, unsupervised, self-supervised or reinforcement? (a) Grouping news articles by topic with no labels. (b) Predicting a masked word in a sentence. (c) A rover learning to drive by trial and error in a simulator, scored on distance covered without hitting rocks. (d) Predicting a house price from its size."

    (a) Unsupervised (clustering). (b) Self-supervised: the label, the hidden word, comes from the data itself.
    (c) Reinforcement: actions, rewards, no example of the right action. (d) Supervised regression.

??? question "3. Using the fruit table, compute by hand the distance from the new fruit (7.9, 6.9) to fruit 2 (7.6, 7.5) and to fruit 8 (8.0, 5.6). Which is nearer?"

    To fruit 2: $\sqrt{(7.6-7.9)^2+(7.5-6.9)^2}=\sqrt{0.09+0.36}=\sqrt{0.45}\approx0.671$. To fruit 8:
    $\sqrt{(0.1)^2+(1.3)^2}=\sqrt{0.01+1.69}=\sqrt{1.70}\approx1.304$. Fruit 2, the orange, is nearer, which agrees
    with the program's output "1-NN says orange". (Fruit 5 at (7.2, 7.4) is at $\sqrt{0.49+0.25}\approx0.860$, and
    the nearest lemon, fruit 6 at (8.5, 5.9), is at $\sqrt{0.36+1.0}\approx1.166$; the nearest of all is fruit 2.)

??? question "4. Why is the training accuracy of 1-NN always 1.0 (when no two identical points have different labels), and why does that tell us nothing?"

    Each training point's nearest neighbour in the training set is itself, at distance 0, so it copies its own
    label. The score measures memory, not generalisation: it would be 1.0 even on data with completely random labels,
    where no learner can do better than chance on new points.

??? question "5. Write the code: change knn_predict so that it uses the Manhattan distance (sum of absolute differences) and run it on the query (8.1, 6.4)."

    ```python
    def manhattan(p, q):
        return sum(abs(a - b) for a, b in zip(p, q))

    def knn_predict_l1(table, x, k=1):
        nearest = sorted(table, key=lambda row: manhattan(row[0], x))[:k]
        votes = Counter(label for _, label in nearest)
        return votes.most_common(1)[0][0]
    ```

    With `TABLE` from the chapter's program, the Manhattan distances from (8.1, 6.4) are 0.9 (fruit 6), 0.9
    (fruit 8), 1.0 (fruit 10), 1.2 (fruit 7), and the nearest orange is fruit 4 at $0.1+1.4=1.5$. So 1-NN, 3-NN and
    5-NN (four lemons and one orange) all still say lemon. Note the tie at 0.9: `sorted` is stable, so the fruit
    that comes first in the table (fruit 6) wins the tie for 1-NN. Ties are worth thinking about whenever distances are rounded or features are
    whole numbers.

??? question "6. In the holdout experiment the best validation accuracy was 0.933, above the best possible accuracy of about 0.856. Explain how that is possible."

    The best possible accuracy is an average over the whole population of points. On a particular set of 60
    points, a model can be right more often than its average by luck, just as a fair coin can come up heads 40 times
    in 60 tosses. Choosing the best of seven values of $k$ picks out the luckiest score. The test score of the chosen
    model, 0.850, is unaffected by this choice and lands near 0.856, as it should.

??? question "7. A student builds a model, measures it on the test set, changes the features, measures again, and repeats ten times, reporting the best test score. What is wrong, and how should they fix it?"

    The test set has been used to make choices, so it has become a validation set, and the best of ten test scores
    is biased upward for the reason in 1.4. Fix: make the choices on a validation set (or by cross-validation on the
    training data), and keep a separate test set that is used once, for the final model only. If the test set has
    already been spent, collect a fresh one.

??? question "8. A model predicts that people who carry lighters are more likely to get lung cancer. Is the model wrong? Should a health campaign ban lighters?"

    The model may be a perfectly good predictor: carrying a lighter is correlated with smoking, and smoking causes
    lung cancer. But the correlation is not a cause: taking the lighter away does nothing if the person still smokes
    (using matches). Smoking is the confounder. Banning lighters is a causal intervention, and the model, trained on
    observational data, says nothing about its effect.

??? question "9. In the no-free-lunch setting, how many target functions are there with 5 binary inputs? If the training set has 3 inputs, for how many target functions is a given learner right on a given unseen input?"

    There are $2^5=32$ inputs, so $2^{32}=4\,294\,967\,296$ target functions. By the pairing argument the learner is
    right on a given unseen input for exactly half of them, $2^{31}=2\,147\,483\,648$, whatever the learner and
    whatever the size of the training set.

??? question "10. The no-free-lunch theorem says every learner averages 1/2 off the training set. Then why does nearest neighbour work so well on the fruit?"

    The theorem averages over all target functions equally, including ones where neighbouring fruit have unrelated
    labels. Real fruit are not like that: shape is strongly related to kind. Nearest neighbour's inductive bias,
    "close means same label", matches this world, so it does well here, and it would do badly in a world (like the
    parity function) where the bias is wrong. Any advantage a learner has comes from assumptions that fit the problem.

??? question "11. Write the code: prove by brute force that the pairing argument holds, by counting, for nearest_neighbour and the input 100 in the chapter's program, the number of target functions on which it is right."

    ```python
    from itertools import product
    from ch01_no_free_lunch import INPUTS, TRAIN, nearest_neighbour

    x = (1, 0, 0)
    right = 0
    for t in product([0, 1], repeat=8):
        f = dict(zip(INPUTS, t))
        data = [(z, f[z]) for z in TRAIN]
        right += nearest_neighbour(data, x) == f[x]
    print(right)        # prints 128, exactly half of 256
    ```

    Run in the folder of the chapter's programs, it prints 128: the learner is right for half the targets, as the
    proof says.

??? question "12. Your 2-class dataset has 950 examples of class A and 50 of class B. A model is 94% accurate on the test set. Is it any good?"

    The baseline "always say A" is 95% accurate, so a 94%-accurate model is worse than doing nothing clever. Whether
    the model is useful depends on what it does with class B: if B is the rare case you care about (a disease, a
    fault), accuracy is the wrong measure, and you want to know how many B cases it finds and how many of its B
    alarms are real. Chapter 7 defines these as recall and precision.

## What you learned

- A learner is a general algorithm that turns examples into a model; by Mitchell's definition, a program learns
  if its performance P at task T improves with experience E.
- Supervised learning has labelled examples (regression for numbers, classification for classes); unsupervised
  learning has only inputs; self-supervised learning makes labels from the data itself; reinforcement learning has
  actions and rewards.
- The nearest-neighbour classifier copies the label of the closest stored example, or lets the $k$ closest vote; it
  assumes that nearby points share labels, and it is sensitive to units and irrelevant features.
- Training accuracy can be meaningless; we fit on a training set, choose on a validation set, and estimate once on a
  test set, because the best of several noisy scores is biased upward.
- Every project follows question, data, model, loss, fit, evaluate, deploy, and most methods are a family of
  models, a loss and an optimiser.
- Learners cannot create information missing from the data, cannot read causes from correlations, and cannot beat
  every other learner on every problem: the no-free-lunch theorem says success comes from assumptions that fit.
- The field grew from Samuel's checkers and Rosenblatt's perceptron, through two winters and backpropagation, to the
  deep-learning era that the 2012 ImageNet result opened.

**Next:** [Chapter 2](02-Data-and-Features.md), the raw material: kinds of features, cleaning, encoding, scaling,
splitting without leaks, and looking at data before modelling it.

## Further reading

- A. L. Samuel, "Some Studies in Machine Learning Using the Game of Checkers", *IBM Journal of Research and
  Development*, 1959.
- T. M. Mitchell, *Machine Learning*, 1997. Chapter 1 gives the definition used here and a full worked design of a
  checkers learner.
- F. Rosenblatt, "The Perceptron: A Probabilistic Model for Information Storage and Organization in the Brain",
  *Psychological Review*, 1958; M. Minsky and S. Papert, *Perceptrons*, 1969.
- D. E. Rumelhart, G. E. Hinton and R. J. Williams, "Learning representations by back-propagating errors", *Nature*,
  1986.
- A. Krizhevsky, I. Sutskever and G. E. Hinton, "ImageNet Classification with Deep Convolutional Neural Networks",
  *Advances in Neural Information Processing Systems*, 2012; J. Deng et al., "ImageNet: A Large-Scale Hierarchical
  Image Database", CVPR 2009.
- T. Cover and P. Hart, "Nearest Neighbor Pattern Classification", *IEEE Transactions on Information Theory*, 1967:
  the classic analysis of the nearest-neighbour rule.
- D. H. Wolpert, "The Lack of A Priori Distinctions Between Learning Algorithms", *Neural Computation*, 1996.
- S. Shalev-Shwartz and S. Ben-David, *Understanding Machine Learning: From Theory to Algorithms*, 2014. Chapters 2
  and 5 (the learning problem and the no-free-lunch theorem).
- T. Hastie, R. Tibshirani and J. Friedman, *The Elements of Statistical Learning*, 2nd ed., 2009. Chapter 2 compares
  nearest neighbours with least squares.
- C. M. Bishop, *Pattern Recognition and Machine Learning*, 2006, Chapter 1.
- R. Caruana, Y. Lou, J. Gehrke, P. Koch, M. Sturm and N. Elhadad, "Intelligible Models for HealthCare: Predicting
  Pneumonia Risk and Hospital 30-day Readmission", KDD 2015: the asthma and pneumonia example of 1.6.
- J. Pearl and D. Mackenzie, *The Book of Why*, 2018: a readable introduction to causal inference.
- On this site: [Chapter 1 of the Algorithms book](../algorithms/01-What-Is-an-Algorithm.md) (what an algorithm is),
  [sorting by comparison](../algorithms/05-Sorting-by-Comparison.md) and
  [selection](../algorithms/06-Sorting-in-Linear-Time-and-Selection.md) (the cost of finding the $k$ nearest). For
  the math: [math.akadian.ca/books](https://math.akadian.ca/books/).
