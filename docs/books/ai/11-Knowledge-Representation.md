# 11. Knowledge representation

*First-order logic ([Chapter 9](09-First-Order-Logic.md)) tells us how to write sentences and draw conclusions, but not
what to write. A knowledge base about the world needs to say what kinds of things exist and how they are organised,
that a mudstone is a sedimentary rock and a rover has wheels, that actions change some things and leave the rest alone,
that events happen in time, and that birds fly unless we learn otherwise. This chapter answers the question: how do
we organise an agent's knowledge so that it is both expressive and efficient to reason with? You will build a
taxonomy with inheritance, frames with defaults and exceptions, a tableau reasoner for a description logic, the
situation and event calculi, Allen's interval algebra, a stable-model solver for default rules and a small knowledge
graph with rule inference and learned embeddings, and you will see why the expert systems of the 1970s and 1980s
faded and what survived them.*

!!! abstract "In this chapter"
    **You will learn:**

    - what an ontology is: categories, subclass and membership, disjointness and partitions, parts and wholes, and
      inheritance
    - semantic networks and frames, default inheritance with exceptions, and the conflicts it can hit (the Nixon
      diamond)
    - description logics: the syntax and semantics of ALC, a tableau algorithm built from scratch, its correctness,
      and the complexity map from EL to OWL
    - how to represent change and time: the frame problem, successor-state axioms, the event calculus and Allen's
      thirteen interval relations
    - non-monotonic reasoning: the closed world, negation as failure, circumscription, default logic and stable
      models (answer set programming)
    - knowledge graphs as data structures (triples, queries, RDFS rules, TransE embeddings), and an honest account of
      why expert systems such as MYCIN faded

    **You need:** [Chapter 9](09-First-Order-Logic.md) (first-order logic, forward chaining, Prolog's negation as
    failure); [Chapter 7](07-Constraint-Satisfaction.md) (constraint propagation) for the interval algebra in 11.3;
    a little NumPy and gradient descent ([Machine learning, Chapter 5](../machine-learning/05-Optimization.md)) for
    the embeddings in 11.5.

    **Levels:** 11.1 is beginner; 11.2 is intermediate, with an advanced section on the tableau proof; 11.3 and 11.4
    are intermediate; 11.5 is beginner to intermediate.

## 11.1 Ontologies and categories; inheritance

### The problem: what is there?

A rover's knowledge base must contain facts like "Rock42 is a mudstone". Is that enough to answer "is Rock42 a rock?"
Only if the knowledge base also knows that mudstones are sedimentary rocks and sedimentary rocks are rocks. Is it
enough to answer "is Rock42 a basalt?" Only if it knows that sedimentary and igneous rocks are different things. A
human never writes these down; they are part of what "mudstone" means. A program must be told.

An **ontology** (from the philosophers' word for the study of what exists) is a formal description of the kinds of
things in a domain and the relations between them. A **general** or **upper ontology** describes the most general
categories (objects, events, times, places, substances, numbers) that every domain shares; a **domain ontology** adds
the categories of one field, such as geology or medicine. Figure 11.1 shows a small one. Writing ontologies is called
**ontological engineering**, and its main lesson, learned the hard way, is that the general categories are much harder
to get right than they look.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 285" role="img" aria-label="A small upper ontology as a tree. Thing splits into AbstractObject, PhysicalObject and Event. AbstractObject has Number, Set and Category. PhysicalObject has Object and Substance. Event has Process and Interval. Object has Rock and Machine. Rock has Igneous, Sedimentary and Metamorphic. Machine has Rover and Instrument.">
<line x1="320" y1="30" x2="110" y2="71" stroke="currentColor"/>
<line x1="320" y1="30" x2="330" y2="71" stroke="currentColor"/>
<line x1="320" y1="30" x2="540" y2="71" stroke="currentColor"/>
<line x1="110" y1="90" x2="40" y2="131" stroke="currentColor"/>
<line x1="110" y1="90" x2="110" y2="131" stroke="currentColor"/>
<line x1="110" y1="90" x2="180" y2="131" stroke="currentColor"/>
<line x1="330" y1="90" x2="280" y2="131" stroke="currentColor"/>
<line x1="330" y1="90" x2="390" y2="131" stroke="currentColor"/>
<line x1="540" y1="90" x2="500" y2="131" stroke="currentColor"/>
<line x1="540" y1="90" x2="590" y2="131" stroke="currentColor"/>
<line x1="280" y1="150" x2="230" y2="191" stroke="currentColor"/>
<line x1="280" y1="150" x2="350" y2="191" stroke="currentColor"/>
<line x1="230" y1="210" x2="130" y2="251" stroke="currentColor"/>
<line x1="230" y1="210" x2="220" y2="251" stroke="currentColor"/>
<line x1="230" y1="210" x2="315" y2="251" stroke="currentColor"/>
<line x1="350" y1="210" x2="410" y2="251" stroke="currentColor"/>
<line x1="350" y1="210" x2="500" y2="251" stroke="currentColor"/>
<text x="320" y="25" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">Thing</text>
<text x="110" y="85" font-size="12" text-anchor="middle" fill="currentColor">AbstractObject</text>
<text x="330" y="85" font-size="12" text-anchor="middle" fill="currentColor">PhysicalObject</text>
<text x="540" y="85" font-size="12" text-anchor="middle" fill="currentColor">Event</text>
<text x="40" y="145" font-size="12" text-anchor="middle" fill="currentColor">Number</text>
<text x="110" y="145" font-size="12" text-anchor="middle" fill="currentColor">Set</text>
<text x="180" y="145" font-size="12" text-anchor="middle" fill="currentColor">Category</text>
<text x="280" y="145" font-size="12" text-anchor="middle" fill="currentColor">Object</text>
<text x="390" y="145" font-size="12" text-anchor="middle" fill="currentColor">Substance</text>
<text x="500" y="145" font-size="12" text-anchor="middle" fill="currentColor">Process</text>
<text x="590" y="145" font-size="12" text-anchor="middle" fill="currentColor">Interval</text>
<rect x="200" y="191" width="60" height="22" rx="5" fill="#eea66f" fill-opacity="0.35" stroke="currentColor"/>
<text x="230" y="206" font-size="12" text-anchor="middle" fill="currentColor">Rock</text>
<rect x="315" y="191" width="70" height="22" rx="5" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor"/>
<text x="350" y="206" font-size="12" text-anchor="middle" fill="currentColor">Machine</text>
<text x="130" y="265" font-size="12" text-anchor="middle" fill="currentColor">Igneous</text>
<text x="220" y="265" font-size="12" text-anchor="middle" fill="currentColor">Sedimentary</text>
<text x="315" y="265" font-size="12" text-anchor="middle" fill="currentColor">Metamorphic</text>
<text x="410" y="265" font-size="12" text-anchor="middle" fill="currentColor">Rover</text>
<text x="500" y="265" font-size="12" text-anchor="middle" fill="currentColor">Instrument</text>
<path d="M105,272 Q220,284 345,272" fill="none" stroke="#7ccf9a" stroke-width="2" stroke-dasharray="4 3"/>
<text x="560" y="210" font-size="11" text-anchor="middle" fill="currentColor">green: a partition</text>
</svg>
<figcaption>Figure 11.1. A small upper ontology with a geology and machine fragment. Every line is a subclass link
(the child is a kind of the parent). The three rock classes form a partition of Rock: every rock is in exactly one of
them.</figcaption>
</figure>

### Categories as predicates and as objects

The basic unit is the **category** (also called a *class* or *concept*): Rock, Mudstone, Rover. In first-order logic a
category can be a one-place predicate, $\mathit{Mudstone}(x)$. But we also want to say things *about* categories:
"mudstone is a kind of sedimentary rock", "Basalt has 13 known examples in our collection", "Rover is a category of
machine". For that, it is convenient to turn the category into an object, a step called **reification** (from the Latin
*res*, thing), and use relations between objects:

- **membership**: $\mathit{Rock42} \in \mathit{Mudstones}$ ("Rock42 is a mudstone");
- **subclass**: $\mathit{Mudstones} \subset \mathit{SedimentaryRocks}$ ("every mudstone is a sedimentary rock").

The two are different, and confusing them was a classic error of early systems: Rock42 is a member of Mudstones but
not a subclass of it; Mudstones is a subclass of Rocks but not a member of it (it is a member of the category of rock
categories, if we want one).

**Inheritance** is the main inference this organisation buys. A property stated once for a category holds for every
member of every subclass: if all rocks have a density, then Rock42 has a density. Formally it is just a chain of
implications, $\forall x\, (\mathit{Mudstone}(x) \Rightarrow \mathit{SedimentaryRock}(x))$ and so on, but organised as
a hierarchy it becomes cheap: to find the categories of an object, follow subclass links upward. The program computes
this **transitive closure** of the subclass relation.

### Disjointness, exhaustiveness, partitions

Three relations between categories carry a lot of knowledge:

- categories are **disjoint** if no object belongs to two of them (igneous and sedimentary rocks; rocks and machines);
- a set of categories is an **exhaustive decomposition** of a category if every member of the category belongs to at
  least one of them;
- a **partition** is a disjoint exhaustive decomposition: every member belongs to exactly one.

In logic, disjointness of $A$ and $B$ is $\forall x\, \lnot(A(x) \land B(x))$; exhaustiveness of $\{A_1, \ldots, A_k\}$
for $C$ is $\forall x\, (C(x) \Rightarrow A_1(x) \lor \cdots \lor A_k(x))$. With these, a reasoner can detect errors:

```
1. A taxonomy
  Rock42   types: Mudstone, PhysicalObject, Rock, SedimentaryRock, Thing
  Rock7    types: Basalt, IgneousRock, PhysicalObject, Rock, Thing
  Odd1     types: Basalt, IgneousRock, PhysicalObject, Rock, Sandstone, SedimentaryRock, Thing   <- violates disjointness [['IgneousRock', 'SedimentaryRock']]
  Percy    types: Machine, PhysicalObject, Rover, Thing
  SuperCam types: Instrument, Machine, PhysicalObject, Thing
  Mudstone is a subclass of Rock: True | Basalt is a subclass of SedimentaryRock: False
  partition of Rock into ['IgneousRock', 'SedimentaryRock', 'MetamorphicRock']: every leaf rock class is covered: True
  parts of Percy: ['Arm', 'Drill', 'Mast', 'SuperCam', 'Wheel3']
```

Someone recorded sample Odd1 as both a basalt and a sandstone; the disjointness axiom catches the contradiction.
(Whether the axiom is *true* is another matter: geologists know rocks that sit on the boundary between classes, and a
good ontology says so instead of forcing a choice. Natural categories rarely have crisp definitions, a point
philosophers from Wittgenstein on, and psychologists studying prototypes, have made at length.)

### Parts, stuff and measures

Not every hierarchy is a hierarchy of kinds. **PartOf** relates an object to a larger object it is a component of: the
SuperCam instrument is part of the mast, the mast is part of the rover. PartOf is **transitive**, so the program's
`parts("Percy")` follows it to every component, including the drill, which is part of the arm. It is also different
from subclass in a way that matters: a property of the rover (its mass) is *not* inherited by its parts.

Two other ideas recur in every upper ontology. **Substances** (stuff such as water, sand, basalt as a material) differ
from **objects**: half a litre of water is still water, but half a rover is not a rover. Properties that survive
division are called *intrinsic* (density, colour), and those that do not are *extrinsic* (mass, shape). And
**measures** (5 metres, 300 kelvin) are best treated as objects produced by functions of a unit, $\mathit{Metres}(5)$,
so that $\mathit{Metres}(5) = \mathit{Centimetres}(500)$ can be stated and used.

### Ontologies in the large

Big ontologies exist. **Cyc**, begun by Douglas Lenat in 1984, set out to encode the common sense of an ordinary adult
by hand. **WordNet** (George Miller and colleagues, Princeton, from the 1980s) organises English words into sets of
synonyms linked by hypernym ("is a kind of") and meronym ("is part of") relations, and was used throughout natural
language processing ([Chapter 16](16-Natural-Language-Processing.md)). In medicine, **SNOMED CT** is a large clinical
terminology written in a description logic (11.2), and the **Gene Ontology** describes gene functions for biology.
The experience of these projects is mixed in an instructive way: domain ontologies built by communities for a specific
purpose have been very successful; the dream of one hand-written ontology of all common sense has not been reached.

### The taxonomy and frames program

```python
--8<-- "books/ai/ch11_inheritance.py"
```

```
1. A taxonomy
  Rock42   types: Mudstone, PhysicalObject, Rock, SedimentaryRock, Thing
  Rock7    types: Basalt, IgneousRock, PhysicalObject, Rock, Thing
  Odd1     types: Basalt, IgneousRock, PhysicalObject, Rock, Sandstone, SedimentaryRock, Thing   <- violates disjointness [['IgneousRock', 'SedimentaryRock']]
  Percy    types: Machine, PhysicalObject, Rover, Thing
  SuperCam types: Instrument, Machine, PhysicalObject, Thing
  Mudstone is a subclass of Rock: True | Basalt is a subclass of SedimentaryRock: False
  partition of Rock into ['IgneousRock', 'SedimentaryRock', 'MetamorphicRock']: every leaf rock class is covered: True
  parts of Percy: ['Arm', 'Drill', 'Mast', 'SuperCam', 'Wheel3']

2. Frames and default inheritance
  Tweety flies     = True      from Bird
  Tweety legs      = 2         from Bird
  Tweety covering  = feathers  from Bird
  Opus   flies     = False     from Penguin
  Opus   legs      = 1         from Opus
  Opus   swims     = True      from Penguin
  Opus   covering  = feathers  from Bird
  Nixon  pacifist  = CONFLICT  from Quaker says True, Republican says False
```

Part 2 of the output, on frames, is explained in 11.2.

## 11.2 Semantic networks and frames; description logics

### Semantic networks

In 1968 Ross Quillian proposed a model of human memory in which concepts are nodes of a graph and links connect them:
"canary is-a bird", "bird has wings", "bird can fly". To answer "can a canary fly?" you walk up the is-a links until
you find a "can fly" link. Such a **semantic network** is a picture of a set of logical facts, but the picture
suggests the algorithm: inheritance is graph traversal, and finding how two concepts are related is a search for a
path between them.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 260" role="img" aria-label="Two semantic networks. Left: Opus is an instance of Penguin, which is a kind of Bird; Bird has flies yes and legs 2; Penguin has flies no; Opus has legs 1. Right: Nixon is an instance of both Quaker and Republican; Quaker says pacifist yes, Republican says pacifist no, so the value for Nixon is in conflict.">
<ellipse cx="120" cy="40" rx="50" ry="20" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/>
<text x="120" y="45" font-size="13" text-anchor="middle" fill="currentColor">Bird</text>
<text x="180" y="36" font-size="12" fill="currentColor">flies: yes</text>
<text x="180" y="52" font-size="12" fill="currentColor">legs: 2</text>
<ellipse cx="120" cy="130" rx="50" ry="20" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/>
<text x="120" y="135" font-size="13" text-anchor="middle" fill="currentColor">Penguin</text>
<text x="180" y="126" font-size="12" fill="currentColor">flies: no</text>
<text x="180" y="142" font-size="12" fill="currentColor">swims: yes</text>
<rect x="80" y="200" width="80" height="34" rx="6" fill="#eea66f" fill-opacity="0.45" stroke="currentColor"/>
<text x="120" y="222" font-size="13" text-anchor="middle" fill="currentColor">Opus</text>
<text x="180" y="222" font-size="12" fill="currentColor">legs: 1</text>
<line x1="120" y1="110" x2="120" y2="62" stroke="currentColor" stroke-width="1.5"/>
<polygon points="120,60 115,70 125,70" fill="currentColor"/>
<text x="112" y="90" font-size="11" text-anchor="end" fill="currentColor">is-a</text>
<line x1="120" y1="200" x2="120" y2="152" stroke="currentColor" stroke-width="1.5"/>
<polygon points="120,150 115,160 125,160" fill="currentColor"/>
<text x="112" y="180" font-size="11" text-anchor="end" fill="currentColor">instance-of</text>
<line x1="320" y1="15" x2="320" y2="245" stroke="currentColor" stroke-opacity="0.3"/>
<ellipse cx="420" cy="60" rx="55" ry="20" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/>
<text x="420" y="65" font-size="13" text-anchor="middle" fill="currentColor">Quaker</text>
<text x="420" y="98" font-size="12" text-anchor="middle" fill="currentColor">pacifist: yes</text>
<ellipse cx="570" cy="60" rx="58" ry="20" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/>
<text x="570" y="65" font-size="13" text-anchor="middle" fill="currentColor">Republican</text>
<text x="570" y="98" font-size="12" text-anchor="middle" fill="currentColor">pacifist: no</text>
<rect x="455" y="190" width="80" height="34" rx="6" fill="#eea66f" fill-opacity="0.45" stroke="currentColor"/>
<text x="495" y="212" font-size="13" text-anchor="middle" fill="currentColor">Nixon</text>
<text x="495" y="245" font-size="12" text-anchor="middle" fill="currentColor">pacifist: ? (conflict)</text>
<line x1="480" y1="190" x2="428" y2="82" stroke="currentColor" stroke-width="1.5"/>
<polygon points="427,80 425,92 434,88" fill="currentColor"/>
<line x1="510" y1="190" x2="562" y2="82" stroke="currentColor" stroke-width="1.5"/>
<polygon points="563,80 556,88 565,92" fill="currentColor"/>
</svg>
<figcaption>Figure 11.2. Default inheritance. Left: the most specific value wins, so Opus does not fly (from Penguin)
and has one leg (his own slot), but still has feathers (from Bird). Right: the Nixon diamond, where two
incomparable classes give opposite defaults and specificity cannot decide.</figcaption>
</figure>

The weakness of early networks was that nobody said exactly what a link meant. William Woods's paper "What's in a
link" (1975) and Ronald Brachman's "What IS-A is and isn't" (1983) catalogued the confusion: the same "is-a" arrow was
used for membership, subclass, "is typically", and even "is a part of". Different programs drew different conclusions
from the same picture. The cure, worked out over the next decade, was to give networks a precise logical semantics,
which led to description logics.

### Frames, slots and defaults

Marvin Minsky's "A framework for representing knowledge" (1975) proposed **frames**: a frame describes a stereotyped
object or situation, with **slots** for its properties and, often, **default values** that hold unless overridden. A
"bird" frame has a slot *flies* with default *yes*. Frames may also have **procedural attachments**: code that runs
when a slot is read or written (compute the age from the birth date; warn when a temperature is set too high). Frames
became the basis of many expert-system shells and of object-oriented programming, where a class with fields and
default values is nearly a frame.

Defaults are where frames go beyond classical logic. "Birds fly" is not a universal law, because penguins do not, and
a logic in which $\forall x\, (\mathit{Bird}(x) \Rightarrow \mathit{Flies}(x))$ and $\mathit{Penguin}(\mathit{Opus})$,
$\mathit{Bird}(\mathit{Opus})$, $\lnot\mathit{Flies}(\mathit{Opus})$ are all asserted is inconsistent. Frame systems
handle this by **overriding**: a value stored on a more specific frame wins over one inherited from a more general
frame. The program implements this rule, often called **inferential distance** after David Touretzky's analysis
(1986): collect the frames that hold a value for the slot, keep the most specific (those not above another holder),
and report a conflict if they disagree.

```
2. Frames and default inheritance
  Tweety flies     = True      from Bird
  Tweety legs      = 2         from Bird
  Tweety covering  = feathers  from Bird
  Opus   flies     = False     from Penguin
  Opus   legs      = 1         from Opus
  Opus   swims     = True      from Penguin
  Opus   covering  = feathers  from Bird
  Nixon  pacifist  = CONFLICT  from Quaker says True, Republican says False
```

Opus inherits *flies = False* from Penguin, which overrides Bird; his own slot *legs = 1* overrides everything. But
Nixon is a Quaker (pacifist by default) and a Republican (not pacifist by default), and neither class is more specific
than the other: this is the **Nixon diamond**, the standard example from Reiter and Criscuolo (1981). The program
refuses to choose. Section 11.4 returns to what a logic should conclude here.

### Description logics

**Description logics** (DLs) are the precise descendants of semantic networks and frames. They began with Brachman's
KL-ONE system (Brachman and Schmolze, 1985), and today they are the logics behind the OWL Web Ontology Language and
large medical terminologies. A DL talks about three kinds of thing:

- **concepts** (classes, one-place predicates): $\mathit{Rock}$, $\mathit{Lake}$;
- **roles** (two-place relations): $\mathit{formedIn}$, $\mathit{hasPart}$;
- **individuals** (constants): $\mathit{Rock42}$, $\mathit{Jezero}$.

Complex concepts are built with a small set of **constructors**. The basic DL is called **ALC** ("attributive language
with complements"):

| syntax | read as | meaning in an interpretation $\mathcal{I}$ with domain $\Delta$ |
|---|---|---|
| $A$ | atomic concept | a set $A^{\mathcal{I}} \subseteq \Delta$ |
| $\top$, $\bot$ | everything, nothing | $\Delta$, $\emptyset$ |
| $\lnot C$ | not $C$ | $\Delta \setminus C^{\mathcal{I}}$ |
| $C \sqcap D$ | $C$ and $D$ | $C^{\mathcal{I}} \cap D^{\mathcal{I}}$ |
| $C \sqcup D$ | $C$ or $D$ | $C^{\mathcal{I}} \cup D^{\mathcal{I}}$ |
| $\exists r.C$ | some $r$-successor is a $C$ | $\{x : \text{some } y \text{ with } (x, y) \in r^{\mathcal{I}} \text{ has } y \in C^{\mathcal{I}}\}$ |
| $\forall r.C$ | all $r$-successors are $C$ | $\{x : \text{every } y \text{ with } (x, y) \in r^{\mathcal{I}} \text{ has } y \in C^{\mathcal{I}}\}$ |

So $\mathit{Rock} \sqcap \exists \mathit{formedIn}.\mathit{Lake}$ is "rocks formed in some lake". Every ALC concept is a
first-order formula with one free variable: $\exists r.C$ is $\exists y\, (r(x, y) \land C(y))$. ALC is a
fragment of first-order logic, chosen so that reasoning is decidable (it is a notational variant of the modal logic K,
as Klaus Schild observed in 1991).

A knowledge base has two parts. The **TBox** (terminology) holds **inclusions** $C \sqsubseteq D$ ("every $C$ is a
$D$") and definitions $A \equiv C$ (two inclusions). The **ABox** (assertions) holds facts about individuals,
$\mathit{Mudstone}(\mathit{Rock42})$ and $\mathit{formedIn}(\mathit{Rock42}, \mathit{Lake1})$. The standard reasoning
tasks are:

- **satisfiability**: can concept $C$ have any members in some model of the TBox?
- **subsumption**: does $C \sqsubseteq D$ follow from the TBox? This builds the class hierarchy automatically
  ("classification");
- **instance checking**: is individual $a$ a member of $C$ in every model of the knowledge base?

They reduce to each other. In particular, $C \sqsubseteq D$ holds exactly when $C \sqcap \lnot D$ is unsatisfiable, the
same refutation trick as resolution. So one procedure, a satisfiability test, is all we need.

### The tableau algorithm

*Level: advanced.*

The **tableau** algorithm (Schmidt-Schauß and Smolka, 1991, for ALC) tries to build a model. First put the concept in
**negation normal form** (NNF): push $\lnot$ inward with $\lnot(C \sqcap D) = \lnot C \sqcup \lnot D$, $\lnot(C \sqcup D)
= \lnot C \sqcap \lnot D$, $\lnot \exists r.C = \forall r.\lnot C$ and $\lnot \forall r.C = \exists r.\lnot C$, so that
negation sits only on atomic names. Then grow a tree of individuals, each with a **label**: the set of concepts it must
belong to. Start with one node labelled $\{C\}$, and apply rules until none applies:

1. **$\sqcap$-rule:** if $C_1 \sqcap C_2$ is in a node's label, add $C_1$ and $C_2$.
2. **$\sqcup$-rule:** if $C_1 \sqcup C_2$ is in the label and neither disjunct is, add one of them. This is a choice;
   if it leads to a clash, backtrack and try the other.
3. **$\exists$-rule:** if $\exists r.C$ is in the label, create an $r$-successor node labelled $\{C\}$.
4. **$\forall$-rule:** if $\forall r.C$ is in the label, add $C$ to every $r$-successor.

A **clash** is a label containing both $A$ and $\lnot A$, or $\bot$. The concept is satisfiable if some sequence of
choices leads to a complete, clash-free tree; that tree *is* a model (each node an individual, each atomic concept true
where it appears in a label).

Take $\exists r.A \sqcap \forall r.\lnot A$: the $\sqcap$-rule gives both conjuncts; the $\exists$-rule makes a successor
labelled $\{A\}$; the $\forall$-rule adds $\lnot A$ to it; clash, and no choices to undo, so it is unsatisfiable. Take
$\exists r.A \sqcap \exists r.B \sqcap \lnot \exists r.(A \sqcap B)$, the test of whether $\exists r.A \sqcap \exists r.B
\sqsubseteq \exists r.(A \sqcap B)$: the NNF of the last conjunct is $\forall r.(\lnot A \sqcup \lnot B)$; there are two
successors, one with $A$ and one with $B$; each receives $\lnot A \sqcup \lnot B$, and the first chooses $\lnot B$,
the second $\lnot A$. No clash: the subsumption fails, and the tree is a counter-model, "something with an $r$-friend
who is $A$ and a different $r$-friend who is $B$, but no friend who is both". (Exercise 4.)

**Theorem.** For ALC concepts (with an empty TBox), the tableau algorithm terminates, and it answers "satisfiable"
exactly when the concept has a model.

*Proof sketch.* *Termination:* every concept added to a label is a subconcept of the input (in NNF), so labels are
subsets of a set of size at most $n$, the length of the input. Each successor's label consists of concepts with
strictly smaller **role depth** (nesting of $\exists$ and $\forall$) than the $\exists$ that created it, so the tree has
depth at most $n$, and each node has at most $n$ successors (one per $\exists$ in its label). The tree is finite and
every rule adds something new, so the run is finite; the choices form a finite search. *Soundness:* a complete
clash-free tree defines an interpretation (domain: the nodes; $A^{\mathcal{I}}$: the nodes whose label contains $A$;
$r^{\mathcal{I}}$: the $r$-edges), and by induction on the structure of concepts every node belongs to every concept in
its label; so the root is in $C^{\mathcal{I}}$. *Completeness:* if $C$ has a model, use it as a guide: map the root to
an element of $C^{\mathcal{I}}$, make each $\sqcup$ choice as that element does, and map each new successor to a witness
in the model. Labels then stay true of their images, so no clash can arise. $\square$

The algorithm explores the tree depth first and only needs to keep one branch in memory, which gives a polynomial-space
procedure; Schmidt-Schauß and Smolka also proved ALC satisfiability **PSPACE-complete**, so nothing fundamentally
better is expected.

**TBoxes and blocking.** With a TBox, each inclusion $C \sqsubseteq D$ means "every individual is in $\lnot C \sqcup
D$", so the reasoner adds that concept to every label. Now a cyclic axiom such as $\mathit{Site} \sqsubseteq \exists
\mathit{linkedTo}.\mathit{Site}$ would create successors forever. The fix is **blocking**: if a node's label is a
subset of an ancestor's label, stop expanding it, because it can reuse the ancestor's successors (in the model, the
link goes back up, making a cycle). With blocking the algorithm terminates again, and satisfiability with respect to a
general TBox is **EXPTIME-complete**. The program prints the blocked node:

```
4. Blocking: Site is satisfiable although Site ⊑ ∃linkedTo.Site asks for an endless chain
  Site, ¬IgneousRock, ¬Rock
      --linkedTo--> Site, ¬IgneousRock, ¬Rock   [blocked]
```

The model is one site linked to itself, or an endless chain of sites; either satisfies the axiom.

### The program on a small geology TBox

The TBox says: mudstone is sedimentary rock, basalt is igneous rock, both kinds are rocks, igneous and sedimentary are
disjoint, a lake deposit is exactly a rock formed in a lake, every lake contains water, and every site links to a site.

```
1. Subsumption and satisfiability with respect to the TBox (tableau nodes: lazy unfolding / naive)
  (Mudstone ⊓ ∃formedIn.Lake) ⊑ LakeDeposit ?          yes  (10 / 115 nodes)
  LakeDeposit ⊑ ∃formedIn.∃contains.Water ?            yes  (43 / 4841 nodes)
  LakeDeposit ⊑ SedimentaryRock ?                      no   (12 / 32 nodes)
  (∀r.A ⊓ ∃r.B) ⊑ ∃r.(A ⊓ B) ?                         yes  (87 / 2457 nodes)
  ∃r.(A ⊓ B) ⊑ (∃r.A ⊓ ∃r.B) ?                         yes  (77 / 3913 nodes)
  (∃r.A ⊓ ∃r.B) ⊑ ∃r.(A ⊓ B) ?                         no   (18 / 36 nodes)
  (Basalt ⊓ Mudstone) satisfiable?                     no   (9 / 41 nodes)
  (∃r.A ⊓ ∀r.¬A) satisfiable?                          no   (39 / 2009 nodes)
  (Basalt ⊓ (Mudstone ⊔ ∃formedIn.Lake)) satisfiable?  yes  (25 / 166 nodes)
  Site satisfiable?                                    yes  (10 / 24 nodes)
```

Three things to notice. First, the reasoner *derived* the class hierarchy: a mudstone formed in a lake is a lake
deposit, and a lake deposit was formed in something that contains water, though no axiom says either directly. Second,
"no" answers come with a model, which explains them:

```
3. A counter-model: LakeDeposit ⊓ ¬SedimentaryRock is satisfiable, so LakeDeposit ⋢ SedimentaryRock
  LakeDeposit, Rock, ¬SedimentaryRock
      --formedIn--> Lake, ¬IgneousRock, ¬Rock
          --contains--> Water, ¬IgneousRock, ¬Rock
```

The TBox never says a lake deposit must be sedimentary (a geologist would add that axiom; the reasoner shows us it is
missing). Third, the node counts. The naive reasoner adds every inclusion, as a disjunction, to every node, and
branches on each; that costs thousands of nodes even for tiny questions. **Lazy unfolding** treats an inclusion with
an atomic left side, $A \sqsubseteq D$, as a rule "if $A$ is in the label, add $D$", with no disjunction at all. That
single optimisation cut the work by factors of 10 to 100 here. Real reasoners (FaCT++, HermiT, Pellet, Konclude) pile
up many more: absorption of general axioms into such rules, dependency-directed backtracking, caching of node labels,
and model merging. With them, classifying ontologies with hundreds of thousands of classes is routine.

### The complexity map, and OWL

Description-logic research has mapped, constructor by constructor, how expressiveness costs decidability and time:

- **EL** ($\sqcap$, $\exists$ and $\top$ only) has polynomial-time subsumption even with general TBoxes (Baader, Brandt
  and Lutz, 2005). SNOMED CT is written in a member of the EL family, which is why it can be classified quickly despite
  its size.
- **ALC** is PSPACE-complete for concepts and EXPTIME-complete with general TBoxes.
- Adding number restrictions ("at least 6 wheels"), inverse roles ("partOf" as the inverse of "hasPart"), role
  hierarchies, transitive roles and nominals (named individuals inside concepts) gives **SROIQ**, the logic of OWL 2
  DL (W3C, 2009), whose satisfiability is N2EXPTIME-complete, yet practical on real ontologies.
- Some combinations (for instance unrestricted role composition) make reasoning undecidable, which is why OWL imposes
  syntactic restrictions.

DLs and the logic programs of [Chapter 9](09-First-Order-Logic.md) differ in one basic assumption. A DL reasons under
the **open-world assumption**: if the ABox does not say Rock7 was formed in a lake, that is unknown, not false. A
database or Prolog uses the closed world. Both are right for different jobs: an ontology describes what must be true of
any world; a database records what we have observed. Section 11.4 treats the closed world as a kind of default.

### The tableau program

```python
--8<-- "books/ai/ch11_tableau.py"
```

```
1. Subsumption and satisfiability with respect to the TBox (tableau nodes: lazy unfolding / naive)
  (Mudstone ⊓ ∃formedIn.Lake) ⊑ LakeDeposit ?          yes  (10 / 115 nodes)
  LakeDeposit ⊑ ∃formedIn.∃contains.Water ?            yes  (43 / 4841 nodes)
  LakeDeposit ⊑ SedimentaryRock ?                      no   (12 / 32 nodes)
  (∀r.A ⊓ ∃r.B) ⊑ ∃r.(A ⊓ B) ?                         yes  (87 / 2457 nodes)
  ∃r.(A ⊓ B) ⊑ (∃r.A ⊓ ∃r.B) ?                         yes  (77 / 3913 nodes)
  (∃r.A ⊓ ∃r.B) ⊑ ∃r.(A ⊓ B) ?                         no   (18 / 36 nodes)
  (Basalt ⊓ Mudstone) satisfiable?                     no   (9 / 41 nodes)
  (∃r.A ⊓ ∀r.¬A) satisfiable?                          no   (39 / 2009 nodes)
  (Basalt ⊓ (Mudstone ⊔ ∃formedIn.Lake)) satisfiable?  yes  (25 / 166 nodes)
  Site satisfiable?                                    yes  (10 / 24 nodes)

2. The model found for Basalt ⊓ (Mudstone ⊔ ∃formedIn.Lake)
  Basalt, IgneousRock, LakeDeposit, Rock, ¬SedimentaryRock
      --formedIn--> Lake, ¬IgneousRock, ¬Rock
          --contains--> Water, ¬IgneousRock, ¬Rock

3. A counter-model: LakeDeposit ⊓ ¬SedimentaryRock is satisfiable, so LakeDeposit ⋢ SedimentaryRock
  LakeDeposit, Rock, ¬SedimentaryRock
      --formedIn--> Lake, ¬IgneousRock, ¬Rock
          --contains--> Water, ¬IgneousRock, ¬Rock

4. Blocking: Site is satisfiable although Site ⊑ ∃linkedTo.Site asks for an endless chain
  Site, ¬IgneousRock, ¬Rock
      --linkedTo--> Site, ¬IgneousRock, ¬Rock   [blocked]
```

## 11.3 Events, time, and change: situation calculus, event calculus briefly

*Level: intermediate.*

### The frame problem

Logic is timeless: a sentence is true or false, full stop. But the world changes. After the rover drives from Base to
Rim, $\mathit{At}(\mathit{Base})$ is false and $\mathit{At}(\mathit{Rim})$ is true. The planners of
[Chapter 10](10-Planning.md) handled this with a procedure (delete, then add) outside the logic. Can logic itself
describe change?

The obvious fix is to give every changing fact, a **fluent**, an extra argument saying *when* it holds. That raises
the question that John McCarthy and Patrick Hayes named the **frame problem** in 1969. Describing what an action
*changes* is easy. But logic also needs to be told everything the action does *not* change: driving does not change
the arm's position, the samples collected, the time of sunset, the colour of the rocks. Writing one **frame axiom**
per action and unchanged fluent costs about $A \times F$ axioms for $A$ actions and $F$ fluents, nearly all of them
dull, and every new action needs new ones for every fluent. Two cousins of the problem are the **qualification
problem** (an action's preconditions have endless exceptions: the drive works unless a wheel is stuck, unless the
battery is flat, unless...) and the **ramification problem** (actions have indirect effects: driving moves the camera
too, because the camera is part of the rover).

### Situation calculus and successor-state axioms

The **situation calculus** (McCarthy, 1963; McCarthy and Hayes, 1969) adds terms for **situations**: $S_0$ is the
initial situation, and $\mathit{do}(a, s)$ is the situation after doing action $a$ in situation $s$. A history is a
nested term: $\mathit{do}(\mathit{Drill}, \mathit{do}(\mathit{Unstow}, \mathit{do}(\mathit{Drive}(\mathit{Base},
\mathit{Rim}), S_0)))$. Fluents take a situation argument: $\mathit{At}(p, s)$. A **precondition axiom** says when an
action is possible, $\mathit{Poss}(a, s)$, and the effects are described by axioms about $\mathit{do}(a, s)$.

Raymond Reiter (1991) gave the standard solution to the frame problem, building on work by Edwin Pednault, Lenhart
Schubert and Andrew Haas. For each fluent, write *one* **successor-state axiom** that says exactly when it is true after
any action: it becomes true if an action made it true, and it stays true if it was true and no action made it false.

$$
\mathit{At}(p, \mathit{do}(a, s)) \;\Leftrightarrow\; \exists q\, \big(a = \mathit{Drive}(q, p)\big) \;\lor\; \Big(\mathit{At}(p, s) \land \lnot \exists q\, \big(a = \mathit{Drive}(p, q)\big)\Big).
$$

The second disjunct is the frame axiom, folded into the fluent's own definition: $F$ axioms in total, not $A \times F$,
and each one mentions only the actions that affect its fluent. (It relies on knowing all those actions, a
completeness assumption that is the logical version of the STRIPS assumption, and on **unique names** for actions, so
that $\mathit{Drive}(q, p) \neq \mathit{Drill}$.) To answer "does $F$ hold after this history?", apply the axiom to
peel off the last action, then the one before, back to $S_0$. This is **regression**, the same idea as backward
planning in [Chapter 10](10-Planning.md), and our program's `holds` function is exactly that recursion:

```
1. Situation calculus
  situation: do(Drive(Rim,Delta), do(Stow, do(Drill, do(Unstow, do(Drive(Base,Rim), S0)))))
  At(Delta) holds: True
  At(Rim) holds: False
  At(Base) holds: False
  Sampled(Rim) holds: True
  Sampled(Delta) holds: False
  ArmStowed holds: True
  driving with the arm unstowed is refused by the precondition axiom: Drive(Rim,Delta) in do(Unstow, do(Drive(Base,Rim), S0))
```

Trace $\mathit{Sampled}(\mathit{Rim})$ in the final situation. The last action is a drive, which neither samples nor
unsamples, so the axiom passes the question back; the same for Stow; at Drill, the axiom asks whether the rover was at
Rim with the arm out just before, which regression to $\mathit{do}(\mathit{Unstow}, \ldots)$ confirms. The situation
calculus was also the basis of the GOLOG family of agent programming languages (Levesque, Reiter and others, 1997), in
which programs are written with actions and tests and executed by regression-based reasoning.

### The event calculus

Situations are branching histories of discrete actions; they do not say *when* things happen or let two things happen
at once. The **event calculus** (Robert Kowalski and Marek Sergot, 1986) uses a time line instead. Its basic predicates
are $\mathit{Happens}(e, t)$ (event $e$ occurs at time $t$), $\mathit{Initiates}(e, f, t)$ and $\mathit{Terminates}(e,
f, t)$ (the event starts or ends fluent $f$), $\mathit{Initially}(f)$ and $\mathit{HoldsAt}(f, t)$. The central axiom
is the commonsense **law of inertia**: a fluent holds at $t$ if an earlier event initiated it and no event in between
terminated it.

$$
\mathit{HoldsAt}(f, t) \;\Leftarrow\; \mathit{Happens}(e, t_1) \land \mathit{Initiates}(e, f, t_1) \land t_1 < t \land \lnot \mathit{Clipped}(t_1, f, t),
$$

where $\mathit{Clipped}(t_1, f, t)$ means some event between $t_1$ and $t$ terminates $f$. (A similar axiom covers
fluents true initially.) The $\lnot$ in front of $\mathit{Clipped}$ is read as negation as failure: the events in the
narrative are taken to be all the events, which is a closed-world assumption (11.4); formally it is achieved by
circumscription. The program runs a narrative of a rover's afternoon and night:

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 220" role="img" aria-label="A timeline from 0 to 16. Daylight holds from 0 to 10 and again at 16. Heating holds from 2 to 6 and from 13 to 16. Moving holds from 5 to 9. Events are marked: HeaterOn at 1, DriveStart at 4, HeaterOff at 6, DriveStop at 9, SunSet at 10, HeaterOn at 12, SunRise at 15.">
<text x="90" y="44" font-size="12" text-anchor="end" fill="currentColor">Daylight</text>
<rect x="100" y="30" width="330" height="18" fill="#eea66f" fill-opacity="0.7" stroke="currentColor"/>
<rect x="580" y="30" width="30" height="18" fill="#eea66f" fill-opacity="0.7" stroke="currentColor"/>
<text x="90" y="80" font-size="12" text-anchor="end" fill="currentColor">Heating</text>
<rect x="160" y="66" width="150" height="18" fill="#7ccf9a" fill-opacity="0.7" stroke="currentColor"/>
<rect x="490" y="66" width="120" height="18" fill="#7ccf9a" fill-opacity="0.7" stroke="currentColor"/>
<text x="90" y="116" font-size="12" text-anchor="end" fill="currentColor">Moving</text>
<rect x="250" y="102" width="150" height="18" fill="#9cc9ea" fill-opacity="0.7" stroke="currentColor"/>
<line x1="100" y1="150" x2="610" y2="150" stroke="currentColor"/>
<line x1="100" y1="150" x2="100" y2="155" stroke="currentColor"/>
<text x="100" y="167" font-size="11" text-anchor="middle" fill="currentColor">0</text>
<line x1="130" y1="150" x2="130" y2="155" stroke="currentColor"/>
<line x1="160" y1="150" x2="160" y2="155" stroke="currentColor"/>
<text x="160" y="167" font-size="11" text-anchor="middle" fill="currentColor">2</text>
<line x1="190" y1="150" x2="190" y2="155" stroke="currentColor"/>
<line x1="220" y1="150" x2="220" y2="155" stroke="currentColor"/>
<text x="220" y="167" font-size="11" text-anchor="middle" fill="currentColor">4</text>
<line x1="250" y1="150" x2="250" y2="155" stroke="currentColor"/>
<line x1="280" y1="150" x2="280" y2="155" stroke="currentColor"/>
<text x="280" y="167" font-size="11" text-anchor="middle" fill="currentColor">6</text>
<line x1="310" y1="150" x2="310" y2="155" stroke="currentColor"/>
<line x1="340" y1="150" x2="340" y2="155" stroke="currentColor"/>
<text x="340" y="167" font-size="11" text-anchor="middle" fill="currentColor">8</text>
<line x1="370" y1="150" x2="370" y2="155" stroke="currentColor"/>
<line x1="400" y1="150" x2="400" y2="155" stroke="currentColor"/>
<text x="400" y="167" font-size="11" text-anchor="middle" fill="currentColor">10</text>
<line x1="430" y1="150" x2="430" y2="155" stroke="currentColor"/>
<line x1="460" y1="150" x2="460" y2="155" stroke="currentColor"/>
<text x="460" y="167" font-size="11" text-anchor="middle" fill="currentColor">12</text>
<line x1="490" y1="150" x2="490" y2="155" stroke="currentColor"/>
<line x1="520" y1="150" x2="520" y2="155" stroke="currentColor"/>
<text x="520" y="167" font-size="11" text-anchor="middle" fill="currentColor">14</text>
<line x1="550" y1="150" x2="550" y2="155" stroke="currentColor"/>
<line x1="580" y1="150" x2="580" y2="155" stroke="currentColor"/>
<text x="580" y="167" font-size="11" text-anchor="middle" fill="currentColor">16</text>
<line x1="130" y1="22" x2="130" y2="178" stroke="currentColor" stroke-opacity="0.35" stroke-dasharray="3 3"/>
<text x="130" y="190" font-size="11" text-anchor="middle" fill="currentColor">HeaterOn</text>
<line x1="220" y1="22" x2="220" y2="196" stroke="currentColor" stroke-opacity="0.35" stroke-dasharray="3 3"/>
<text x="220" y="208" font-size="11" text-anchor="middle" fill="currentColor">DriveStart</text>
<line x1="280" y1="22" x2="280" y2="178" stroke="currentColor" stroke-opacity="0.35" stroke-dasharray="3 3"/>
<text x="280" y="190" font-size="11" text-anchor="middle" fill="currentColor">HeaterOff</text>
<line x1="370" y1="22" x2="370" y2="196" stroke="currentColor" stroke-opacity="0.35" stroke-dasharray="3 3"/>
<text x="370" y="208" font-size="11" text-anchor="middle" fill="currentColor">DriveStop</text>
<line x1="400" y1="22" x2="400" y2="178" stroke="currentColor" stroke-opacity="0.35" stroke-dasharray="3 3"/>
<text x="400" y="190" font-size="11" text-anchor="middle" fill="currentColor">SunSet</text>
<line x1="460" y1="22" x2="460" y2="196" stroke="currentColor" stroke-opacity="0.35" stroke-dasharray="3 3"/>
<text x="460" y="208" font-size="11" text-anchor="middle" fill="currentColor">HeaterOn</text>
<line x1="550" y1="22" x2="550" y2="178" stroke="currentColor" stroke-opacity="0.35" stroke-dasharray="3 3"/>
<text x="550" y="190" font-size="11" text-anchor="middle" fill="currentColor">SunRise</text>
<text x="610" y="167" font-size="11" text-anchor="end" fill="currentColor">time</text>
</svg>
<figcaption>Figure 11.3. The event-calculus narrative computed by the program. Each fluent starts to hold just after the
event that initiates it, and persists, by inertia, until an event terminates it. The heater switched on at 12 is never
switched off in the narrative, so Heating holds to the end.</figcaption>
</figure>

```
2. Event calculus: which fluents hold at each time
   t  Daylight  Heating   Moving    events
   0  yes       .         .         
   1  yes       .         .         HeaterOn
   2  yes       yes       .         
  ...
  10  yes       .         .         SunSet
  11  .         .         .         
  ...
  15  .         yes       .         SunRise
  16  yes       yes       .         
```

The event calculus handles concurrent events, continuous change (a battery's charge rising during a charging
interval, with extra axioms) and narratives in which only some events are known. It is used in commonsense reasoning
research and in formal descriptions of business processes and legal-style rules, and it is a natural partner for the
scheduling of [10.5](10-Planning.md#105-hierarchical-task-networks-scheduling-with-resources).

### Intervals: Allen's algebra

Often what we know is not the time of each event but how intervals relate: "the heating overlaps the start of the
drive", "the downlink is after the imaging". James Allen (1983) observed that two intervals with distinct endpoints
can stand in exactly 13 relations: 6 pairs of inverses plus *equals* (Figure 11.4).

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 275" role="img" aria-label="Allen's interval relations drawn as pairs of bars: A before B, A meets B, A overlaps B, A starts B, A during B, A finishes B, A equals B, each with its inverse named on the right: after, met-by, overlapped-by, started-by, contains, finished-by, equals.">
<text x="20" y="32" font-size="13" fill="currentColor">A before B</text>
<rect x="200" y="18" width="80" height="10" fill="#eea66f" stroke="currentColor"/>
<rect x="320" y="32" width="100" height="10" fill="#9cc9ea" stroke="currentColor"/>
<text x="440" y="32" font-size="12" fill="currentColor">inverse: after</text>
<text x="20" y="66" font-size="13" fill="currentColor">A meets B</text>
<rect x="200" y="52" width="100" height="10" fill="#eea66f" stroke="currentColor"/>
<rect x="300" y="66" width="120" height="10" fill="#9cc9ea" stroke="currentColor"/>
<text x="440" y="66" font-size="12" fill="currentColor">inverse: met-by</text>
<text x="20" y="100" font-size="13" fill="currentColor">A overlaps B</text>
<rect x="200" y="86" width="130" height="10" fill="#eea66f" stroke="currentColor"/>
<rect x="280" y="100" width="140" height="10" fill="#9cc9ea" stroke="currentColor"/>
<text x="440" y="100" font-size="12" fill="currentColor">inverse: overlapped-by</text>
<text x="20" y="134" font-size="13" fill="currentColor">A starts B</text>
<rect x="250" y="120" width="70" height="10" fill="#eea66f" stroke="currentColor"/>
<rect x="250" y="134" width="170" height="10" fill="#9cc9ea" stroke="currentColor"/>
<text x="440" y="134" font-size="12" fill="currentColor">inverse: started-by</text>
<text x="20" y="168" font-size="13" fill="currentColor">A during B</text>
<rect x="290" y="154" width="70" height="10" fill="#eea66f" stroke="currentColor"/>
<rect x="250" y="168" width="170" height="10" fill="#9cc9ea" stroke="currentColor"/>
<text x="440" y="168" font-size="12" fill="currentColor">inverse: contains</text>
<text x="20" y="202" font-size="13" fill="currentColor">A finishes B</text>
<rect x="350" y="188" width="70" height="10" fill="#eea66f" stroke="currentColor"/>
<rect x="250" y="202" width="170" height="10" fill="#9cc9ea" stroke="currentColor"/>
<text x="440" y="202" font-size="12" fill="currentColor">inverse: finished-by</text>
<text x="20" y="236" font-size="13" fill="currentColor">A equals B</text>
<rect x="250" y="222" width="170" height="10" fill="#eea66f" stroke="currentColor"/>
<rect x="250" y="236" width="170" height="10" fill="#9cc9ea" stroke="currentColor"/>
<text x="440" y="236" font-size="12" fill="currentColor">inverse: equals</text>
<text x="200" y="262" font-size="12" fill="currentColor">orange: interval A    blue: interval B</text>
</svg>
<figcaption>Figure 11.4. Allen's interval relations. Seven are drawn; the inverse of each (swap A and B) gives the
other six, and equals is its own inverse, for 13 in all. Every pair of intervals stands in exactly one of them.</figcaption>
</figure>

Why exactly 13? An interval $A = (a_1, a_2)$ with $a_1 < a_2$ and another $B = (b_1, b_2)$: the relation is decided by
how the four endpoints are ordered. Comparing $a_2$ with $b_1$ (less, equal or greater) and $b_2$ with $a_1$, then
$a_1$ with $b_1$ and $a_2$ with $b_2$ when they overlap, and counting the consistent orderings, gives 13. The program's
`relation` function does exactly these comparisons.

Reasoning with intervals means combining relations. If $A$ meets $B$ and $B$ is during $C$, what is $A$'s relation to
$C$? The **composition table** answers that for all $13 \times 13$ pairs. Allen tabulated it by hand; the program
computes it by brute force, enumerating all triples of intervals with endpoints in $\{0, \ldots, 6\}$ (seven values
are enough to realise any ordering of six endpoints):

```
3. Allen's interval algebra
  composition table: 169 entries (13 x 13)
  before ∘ before = ['before']
  meets ∘ meets = ['before']
  during ∘ before = ['before']
  overlaps ∘ overlaps = ['before', 'meets', 'overlaps']
  before ∘ after = any of the 13
  during ∘ contains = any of the 13
```

A set of intervals with a set of allowed relations between each pair is a constraint network, and Allen's algorithm is
**path consistency**, a stronger cousin of the arc consistency of [Chapter 7](07-Constraint-Satisfaction.md): for every
triple $i, j, k$, restrict the relations allowed between $i$ and $k$ to those in the composition of $(i, j)$ and
$(j, k)$, until nothing changes. Each pass can only delete relations, and there are at most $13 n^2$ to delete, so it
terminates in polynomial time ($O(n^3)$ work per pass).

```
  network: H {overlaps, meets} D;  I {after, met-by} D;  L {after, met-by} I
  path consistent: True;  derived H-to-L: ['before']
  adding L during H: path consistent = False
```

From "the heating overlaps or meets the drive, the imaging follows the drive, the downlink follows the imaging", path
consistency derives that the heating is entirely before the downlink, and it detects that demanding a downlink during
the heating is contradictory. Path consistency is not complete in general: Marc Vilain and Henry Kautz (1986) showed
that deciding whether a network of Allen constraints is consistent is NP-complete, and Nebel and Bürckert (1995) found
the largest tractable subclass (the "ORD-Horn" relations), on which path consistency is complete. Temporal planners
and schedulers use these results directly.

### The events program

```python
--8<-- "books/ai/ch11_events.py"
```

```
1. Situation calculus
  situation: do(Drive(Rim,Delta), do(Stow, do(Drill, do(Unstow, do(Drive(Base,Rim), S0)))))
  At(Delta) holds: True
  At(Rim) holds: False
  At(Base) holds: False
  Sampled(Rim) holds: True
  Sampled(Delta) holds: False
  ArmStowed holds: True
  driving with the arm unstowed is refused by the precondition axiom: Drive(Rim,Delta) in do(Unstow, do(Drive(Base,Rim), S0))

2. Event calculus: which fluents hold at each time
   t  Daylight  Heating   Moving    events
   0  yes       .         .         
   1  yes       .         .         HeaterOn
   2  yes       yes       .         
   3  yes       yes       .         
   4  yes       yes       .         DriveStart
   5  yes       yes       yes       
   6  yes       yes       yes       HeaterOff
   7  yes       .         yes       
   8  yes       .         yes       
   9  yes       .         yes       DriveStop
  10  yes       .         .         SunSet
  11  .         .         .         
  12  .         .         .         HeaterOn
  13  .         yes       .         
  14  .         yes       .         
  15  .         yes       .         SunRise
  16  yes       yes       .         

3. Allen's interval algebra
  composition table: 169 entries (13 x 13)
  before ∘ before = ['before']
  meets ∘ meets = ['before']
  during ∘ before = ['before']
  overlaps ∘ overlaps = ['before', 'meets', 'overlaps']
  before ∘ after = any of the 13
  during ∘ contains = any of the 13
  network: H {overlaps, meets} D;  I {after, met-by} D;  L {after, met-by} I
  path consistent: True;  derived H-to-L: ['before']
  adding L during H: path consistent = False
```

## 11.4 Default reasoning and non-monotonic logic

*Level: intermediate.*

### Jumping to conclusions

People draw conclusions they are prepared to take back. Told that Tweety is a bird, you conclude Tweety flies; told
that Tweety is a penguin, you withdraw it. Told that the timetable lists trains at 10 and at noon, you conclude there
is no train at 3. Classical logic cannot do this, because it is **monotonic**: if $\mathit{KB} \models \alpha$, then
$\mathit{KB} \land \beta \models \alpha$ for any $\beta$. Adding knowledge never removes a conclusion, since the models
of the bigger knowledge base are a subset of the models of the smaller one. A logic in which new information can
remove old conclusions is **non-monotonic**. Every default in 11.2, the closed world of databases and the inertia of
11.3 are examples. Making them precise was a major project of AI in the 1980s; four answers are worth knowing.

### The closed world and negation as failure

The **closed-world assumption** (CWA; Raymond Reiter, 1978) says: an atom that does not follow from the knowledge base
is false. For a database of ground facts it is exactly what we want, and it is what Prolog's `\+` and Datalog's
negation implement ([Chapter 9](09-First-Order-Logic.md)). It is non-monotonic: add $\mathit{Train}(\mathit{Three})$
and the conclusion "no train at 3" disappears. Applied naively to disjunctive knowledge it is inconsistent: from
$\mathit{Ben} \lor \mathit{Cleo}$ ("Ben or Cleo did it") the CWA concludes $\lnot\mathit{Ben}$ (it does not follow) and
$\lnot\mathit{Cleo}$, contradicting the disjunction.

### Circumscription

John McCarthy's **circumscription** (1980) keeps classical logic but changes which models count. Introduce an
**abnormality** predicate and write the default as a classical sentence:

$$
\forall x\, \big(\mathit{Bird}(x) \land \lnot \mathit{Ab}(x) \Rightarrow \mathit{Flies}(x)\big).
$$

Then reason only in the models in which $\mathit{Ab}$ is as small as possible: the **minimal** models with respect to
$\mathit{Ab}$. If nothing forces Tweety to be abnormal, the minimal models make $\mathit{Ab}(\mathit{Tweety})$ false
and so $\mathit{Flies}(\mathit{Tweety})$ true. Add $\forall x\, (\mathit{Penguin}(x) \Rightarrow \mathit{Ab}(x))$ and
$\mathit{Penguin}(\mathit{Tweety})$, and every model, minimal or not, has Tweety abnormal; the conclusion lapses.
Circumscription can be written as a second-order sentence, and in general it is not even semi-decidable, but for
useful special cases it reduces to first-order logic or to the logic programs below.

### Default logic

Reiter's **default logic** (1980) adds rules of a new kind. A **default** is written

$$
\frac{\mathit{Bird}(x) : \mathit{Flies}(x)}{\mathit{Flies}(x)}
$$

and read: "if $\mathit{Bird}(x)$ is believed, and $\mathit{Flies}(x)$ is consistent with what is believed, then believe
$\mathit{Flies}(x)$". The middle part is the **justification**. A set of beliefs that is closed under the classical
consequences and the applicable defaults, and in which every default used remains justified, is an **extension**.

With conflicting defaults there can be several extensions. The Nixon diamond has two: one in which the Quaker default
fired first and blocked the Republican one (Nixon is a pacifist), and one the other way round. What should the agent
believe? A **credulous** reasoner accepts a conclusion that holds in *some* extension (and must then choose one); a
**skeptical** reasoner accepts only what holds in *all* of them, so it believes neither "pacifist" nor "not pacifist".
Neither attitude is right in every application, and making the choice explicit is one of the gains of a formal theory.

### Stable models and answer set programming

The cleanest computational form of default reasoning is the **stable model** semantics of logic programs (Michael
Gelfond and Vladimir Lifschitz, 1988). A **normal logic program** has rules

$$
h \leftarrow b_1, \ldots, b_n, \mathit{not}\; c_1, \ldots, \mathit{not}\; c_m,
$$

where $\mathit{not}$ is negation as failure. The idea is a guess-and-check definition. Guess a set $M$ of atoms. Form
the **reduct** $P^M$: delete every rule that has $\mathit{not}\; c$ with $c \in M$ (the guess says $c$ is true, so the
rule is blocked), and delete the remaining $\mathit{not}$ literals (the guess says they are satisfied). The reduct has
no negation, so it has a least model, computable by forward chaining. $M$ is **stable** if it equals that least model:
the guess reproduces itself.

Our solver tries every subset of the head atoms (fine for a handful; real solvers do much better), and the definition
gives the defaults their meaning:

```
1. Birds fly by default
  Tweety is a bird: 1 stable model(s)
    {Bird(Tweety), Flies(Tweety)}
    Flies(Tweety): credulously yes, skeptically yes
  ... and we learn that Tweety is a penguin: 1 stable model(s)
    {Ab(Tweety), Bird(Tweety), Penguin(Tweety)}
    Flies(Tweety): credulously no, skeptically no
  adding a fact removed a conclusion: the reasoning is non-monotonic
```

Check the first stable model by hand. Guess $M = \{\mathit{Bird}(\mathit{Tweety}), \mathit{Flies}(\mathit{Tweety})\}$.
The rule $\mathit{Flies}(\mathit{Tweety}) \leftarrow \mathit{Bird}(\mathit{Tweety}), \mathit{not}\;
\mathit{Ab}(\mathit{Tweety})$ survives in the reduct (since $\mathit{Ab}(\mathit{Tweety}) \notin M$) as
$\mathit{Flies}(\mathit{Tweety}) \leftarrow \mathit{Bird}(\mathit{Tweety})$. Forward chaining on the reduct from the fact
$\mathit{Bird}(\mathit{Tweety})$ derives exactly $M$. Now guess $M' = \{\mathit{Bird}(\mathit{Tweety})\}$ alone: the
reduct is the same, and its least model contains $\mathit{Flies}(\mathit{Tweety}) \notin M'$, so $M'$ is not stable.

```
2. The Nixon diamond: two conflicting defaults
  Nixon: 2 stable model(s)
    {NonPacifist(Nixon), Quaker(Nixon), Republican(Nixon)}
    {Pacifist(Nixon), Quaker(Nixon), Republican(Nixon)}
    Pacifist(Nixon): credulously yes, skeptically no

3. Programs with no stable model, and negation as failure
  p :- not p: 0 stable model(s)
  closed world: a timetable: 1 stable model(s)
    {NoTrain(Three), Train(Noon), Train(Ten)}
    NoTrain(Three): credulously yes, skeptically yes
```

The diamond has two stable models, the two extensions of default logic, and the program reports both attitudes. The
program $p \leftarrow \mathit{not}\; p$ has none: guessing $p$ true blocks the only rule, so $p$ is not derived; guessing
it false lets the rule derive $p$. Such a rule acts as a **constraint**, and answer set programming uses that on
purpose. The last example shows the method: rules that *generate* choices (each site is visited or skipped, by two
rules that block each other) and a rule that *eliminates* stable models without a good visit. The stable models are
exactly the solutions:

```
4. Choosing: each site is visited or skipped, at least one rock site must be visited
    visit: Ridge
    visit: Delta
    visit: Delta, Ridge
```

This **generate-and-test** style is **answer set programming (ASP)**, a declarative way to solve combinatorial search
problems (planning, scheduling, configuration, puzzles), with solvers such as clingo that combine grounding with
CDCL-style search ([Chapter 8](08-Propositional-Logic-and-SAT.md)). Deciding whether a normal program has a stable model
is NP-complete (Marek and Truszczyński, 1991), so ASP sits at the same level as SAT but with a richer modelling
language.

### Belief revision

A related question is how to change beliefs when new information *contradicts* them, not just adds to them. The AGM
theory (Alchourrón, Gärdenfors and Makinson, 1985) states postulates that any rational revision operator should
satisfy (the result is consistent if the new information is; the new information is believed; as little as possible
is given up, in a precise sense). It is a theory of what a good revision looks like more than an algorithm, and it is
closely related to the default logics above. Probability theory gives another, quantitative answer: Bayes' rule is a
revision operator for degrees of belief ([Chapter 12](12-Probabilistic-Reasoning.md)).

### The stable-model program

```python
--8<-- "books/ai/ch11_defaults.py"
```

```
1. Birds fly by default
  Tweety is a bird: 1 stable model(s)
    {Bird(Tweety), Flies(Tweety)}
    Flies(Tweety): credulously yes, skeptically yes
  ... and we learn that Tweety is a penguin: 1 stable model(s)
    {Ab(Tweety), Bird(Tweety), Penguin(Tweety)}
    Flies(Tweety): credulously no, skeptically no
  adding a fact removed a conclusion: the reasoning is non-monotonic

2. The Nixon diamond: two conflicting defaults
  Nixon: 2 stable model(s)
    {NonPacifist(Nixon), Quaker(Nixon), Republican(Nixon)}
    {Pacifist(Nixon), Quaker(Nixon), Republican(Nixon)}
    Pacifist(Nixon): credulously yes, skeptically no

3. Programs with no stable model, and negation as failure
  p :- not p: 0 stable model(s)
  closed world: a timetable: 1 stable model(s)
    {NoTrain(Three), Train(Noon), Train(Ten)}
    NoTrain(Three): credulously yes, skeptically yes

4. Choosing: each site is visited or skipped, at least one rock site must be visited
    visit: Ridge
    visit: Delta
    visit: Delta, Ridge
```

## 11.5 Knowledge graphs today (as data structures); expert systems and why they faded (MYCIN 1970s)

### Triples

The simplest structure that can hold an ontology and its facts is a set of **triples** (subject, predicate, object):
(Curiosity, landedIn, Gale), (Gale, type, Crater), (Crater, subClassOf, Landform). A set of triples is a directed
graph with labelled edges, a **knowledge graph**. It is a semantic network with the meaning pinned down, and the W3C's
**RDF** (Resource Description Framework, first recommended in 1999) standardised it, with web addresses as names so
that graphs from different sources can be merged. Large public knowledge graphs include DBpedia (Auer and colleagues,
2007), extracted from Wikipedia's infoboxes, and Wikidata (from 2012), edited by volunteers; search engines and many
companies keep their own.

As a data structure, a triple store is a set with **indexes**. Our program indexes by predicate; production stores
keep several orders (subject-predicate-object, predicate-object-subject, and so on) so that any pattern with any
fixed positions can be answered by a lookup. Queries are **basic graph patterns**: triples with variables, all of
which must match, as in the SPARQL query language. Answering one is a join, done by backtracking over the patterns
exactly as Prolog does over goals ([Chapter 9](09-First-Order-Logic.md)):

```
1. A triple store with 21 triples
  rovers, where they landed, and their instruments:
    Curiosity     Gale    ChemCam
    Perseverance  Jezero  SuperCam
  machines before inference: []
```

### Rules over triples

The query "which things are machines?" finds nothing, because no triple says $(x, \mathit{type}, \mathit{Machine})$.
The **RDF Schema** (RDFS) vocabulary gives a few predicates a meaning, by rules that can be forward-chained to a fixed
point like Datalog ([Chapter 9](09-First-Order-Logic.md)):

- $(c, \mathit{subClassOf}, d)$ and $(d, \mathit{subClassOf}, e)$ give $(c, \mathit{subClassOf}, e)$;
- $(x, \mathit{type}, c)$ and $(c, \mathit{subClassOf}, d)$ give $(x, \mathit{type}, d)$;
- $(p, \mathit{subPropertyOf}, q)$ and $(x, p, y)$ give $(x, q, y)$;
- $(p, \mathit{domain}, c)$ and $(x, p, y)$ give $(x, \mathit{type}, c)$; $(p, \mathit{range}, c)$ and $(x, p, y)$ give
  $(y, \mathit{type}, c)$.

```
2. RDFS inference: 35 triples after 3 rounds
  machines after inference: ['Curiosity', 'Ingenuity', 'Perseverance']
  landforms: ['Gale', 'Jezero']
  travelled with: [('Ingenuity', 'Perseverance')]
  instruments: ['ChemCam', 'SuperCam']
```

Rovers and the helicopter are spacecraft, spacecraft are machines; Gale and Jezero are landforms twice over (they are
craters, and they are the range of $\mathit{landedIn}$). Notice that domain and range rules *infer types*, they do not
*check* them: if someone wrote (Gale, landedIn, Curiosity), RDFS would happily conclude that Gale is a spacecraft.
Constraint checking needs a closed-world language on top (the W3C's SHACL is one), which is the open-world versus
closed-world difference of 11.2 again. For more expressive reasoning, OWL ontologies are layered over the same triples.

### Learned representations: TransE

Knowledge graphs are always incomplete. A different tradition fills gaps by learning rather than rules. **TransE**
(Antoine Bordes and colleagues, 2013) gives each entity $e$ a vector $\mathbf{e} \in \mathbb{R}^k$ and each relation $r$
a vector $\mathbf{r}$, and wants $\mathbf{h} + \mathbf{r} \approx \mathbf{t}$ for every true triple $(h, r, t)$: a
relation is a translation in the embedding space. Training minimises a **margin ranking loss**: for a true triple and a
corrupted one (head or tail replaced by a random entity), the energy $\lVert \mathbf{h} + \mathbf{r} - \mathbf{t}
\rVert^2$ of the true triple should be at least a margin $\gamma$ below the corrupted one's,

$$
L = \sum_{(h, r, t)} \max\big(0,\; \gamma + \lVert \mathbf{h} + \mathbf{r} - \mathbf{t} \rVert^2 - \lVert \mathbf{h}' + \mathbf{r} - \mathbf{t}' \rVert^2\big),
$$

by stochastic gradient descent ([Machine learning, Chapter 5](../machine-learning/05-Optimization.md)). The gradient of
$\lVert \mathbf{d} \rVert^2$ is $2\mathbf{d}$, so each step moves the true triple's head and tail together along
$\mathbf{d}$ and the corrupted one's apart. The program trains on twelve places in a line: every "eastOf" fact, and
seven of the eleven "westOf" facts. It then ranks all twelve entities as candidate tails for the four hidden westOf
facts:

```
3. TransE on 12 places in a line: eastOf for all neighbours, westOf for some
  hidden fact P1 westOf P2: true tail ranked 1 of 12
  hidden fact P4 westOf P5: true tail ranked 1 of 12
  hidden fact P7 westOf P8: true tail ranked 1 of 12
  hidden fact P9 westOf P10: true tail ranked 1 of 12
  hidden facts: mean rank 1.00, hits@1 1.00;  training facts: mean rank 1.00
  mean rank on the hidden facts with seeds 1, 2, 3: 1.00, 1.00, 1.00
  cosine(eastOf vector, westOf vector) = -0.82  (an inverse relation should point the other way)
```

Every hidden fact is ranked first. The model was never told that westOf is the inverse of eastOf; the learned vectors
point in nearly opposite directions (cosine $-0.82$), which is the geometric form of that rule. Be careful with the
lesson. This toy has a perfectly regular structure, and getting it to work needed choices (squared distance,
corrupting both heads and tails, enough epochs) that we found by trying; earlier settings ranked the true tail only
third on average. On real graphs, embedding methods are judged by mean rank and hits@$k$ on held-out triples, they make
confident mistakes that a rule would not, and TransE in particular cannot represent some relation patterns (a
symmetric relation would need $\mathbf{r} = 0$). Later models (RotatE, ComplEx and others) address those limits. Rules
and embeddings are complementary: rules are exact and explainable but must be written; embeddings generalise from data
but cannot say why. Today knowledge graphs are also used to ground language models in retrieved facts
([Chapter 17](17-Large-Language-Models.md)).

### Expert systems: what they were

[Chapter 1](01-What-Is-AI.md#knowledge-is-power-expert-systems-the-1970s-and-1980s) told the story of expert systems
and built a small one. Here is the technical anatomy. An expert system had a **knowledge base** of IF-THEN rules
written with a domain expert by a **knowledge engineer**, a **working memory** of facts about the current case, and an
**inference engine** that chained the rules, forwards (as in R1/XCON, which configured computer orders at Digital
Equipment Corporation; McDermott, 1982) or backwards from a hypothesis (as in MYCIN). MYCIN (Edward Shortliffe, Bruce
Buchanan and colleagues, Stanford, 1970s) asked a physician questions about a patient with a blood infection and
recommended antibiotics, using a few hundred rules, each with a **certainty factor** between $-1$ and $1$. It could
explain itself: asked "why?", it showed the rule it was trying to apply; asked "how?", the chain that led to a
conclusion. Separating the rules from the engine also produced **shells** (EMYCIN, the "empty" MYCIN) into which other
domains' rules could be loaded.

### Why they faded

The technical reasons are clearer in hindsight than they were at the time.

1. **The knowledge acquisition bottleneck.** Every rule had to be extracted from an expert by interview, and experts
   are often unable to say how they decide. Large rule bases took years to build.
2. **Brittleness.** A rule base works inside the cases its authors imagined and fails, often silently, just outside;
   there is no graceful "I don't know" (Chapter 1's rock identifier shows this in miniature).
3. **Maintenance.** Rules interact. Adding one to fix a case changes conclusions on others, and as the rule base grows,
   predicting the effect of a change becomes very hard. Large production systems were known for this.
4. **Uncertainty without semantics.** Certainty factors were combined by fixed formulas, such as $\mathrm{CF} = a + b(1
   - a)$ for two positive pieces of evidence. David Heckerman (1986) showed that the scheme matches a consistent
   probabilistic model only under strong independence assumptions that real rule bases violate. A simple case: if two
   rules, each with CF 0.6, are triggered by what is really the same piece of evidence observed twice (two lab tests that
   always agree), the formula gives $0.6 + 0.6 \times 0.4 = 0.84$, counting it twice, while a correct probabilistic
   treatment would not change its belief on the second observation. Probability theory, made practical by Bayesian
   networks, offered a principled replacement ([Chapter 12](12-Probabilistic-Reasoning.md)).
5. **No learning.** The systems did not improve from cases; machine learning methods, which learn decision rules from
   data, gradually took over the classification tasks expert systems had addressed.

What survived is substantial: **business-rule engines** (descendants of OPS5 and Rete, [Chapter 9](09-First-Order-Logic.md)),
which run pricing, eligibility and configuration logic in many companies; **ontologies and description logics**
(11.2), especially in medicine and biology; **knowledge graphs** (above); **Datalog**, for program analysis and data
integration; **constraint and answer set programming** for configuration and scheduling; and the idea of explaining a
conclusion by showing its derivation. And MYCIN's evaluation set an example: in a blinded study published in 1979 (Yu
and colleagues, *JAMA*), outside specialists rated its therapy recommendations for meningitis cases at least as acceptable
as those of the Stanford physicians it was compared with, infectious-disease faculty among them. Yet it was never used
in routine care; the reasons usually given are practical ones, such as the time needed to type in each case and the
difficulty of fitting a consultation program into clinical work.

### The knowledge graph program

```python
--8<-- "books/ai/ch11_knowledge_graph.py"
```

```
1. A triple store with 21 triples
  rovers, where they landed, and their instruments:
    Curiosity     Gale    ChemCam
    Perseverance  Jezero  SuperCam
  machines before inference: []

2. RDFS inference: 35 triples after 3 rounds
  machines after inference: ['Curiosity', 'Ingenuity', 'Perseverance']
  landforms: ['Gale', 'Jezero']
  travelled with: [('Ingenuity', 'Perseverance')]
  instruments: ['ChemCam', 'SuperCam']

3. TransE on 12 places in a line: eastOf for all neighbours, westOf for some
  hidden fact P1 westOf P2: true tail ranked 1 of 12
  hidden fact P4 westOf P5: true tail ranked 1 of 12
  hidden fact P7 westOf P8: true tail ranked 1 of 12
  hidden fact P9 westOf P10: true tail ranked 1 of 12
  hidden facts: mean rank 1.00, hits@1 1.00;  training facts: mean rank 1.00
  mean rank on the hidden facts with seeds 1, 2, 3: 1.00, 1.00, 1.00
  cosine(eastOf vector, westOf vector) = -0.82  (an inverse relation should point the other way)
```

## Check yourself

??? question "1. Write in first-order logic that {IgneousRock, SedimentaryRock, MetamorphicRock} is a partition of Rock. Is it a partition if some rock is unclassified?"

    Disjointness: $\forall x\, \lnot(\mathit{Igneous}(x) \land \mathit{Sedimentary}(x))$, and the same for the other two
    pairs. Exhaustiveness: $\forall x\, (\mathit{Rock}(x) \Rightarrow \mathit{Igneous}(x) \lor \mathit{Sedimentary}(x)
    \lor \mathit{Metamorphic}(x))$. Each class is also a subclass: $\forall x\, (\mathit{Igneous}(x) \Rightarrow
    \mathit{Rock}(x))$, and so on. If some rock belongs to none of the three, exhaustiveness fails, so the three classes
    are disjoint but not a partition. Then a knowledge base with the partition axiom is inconsistent with that rock, and
    the error is in the axiom or in the data.

??? question "2. With the frames of the program, what are Emperor's legs, Opus's height_cm and Emperor's swims, and where does each value come from?"

    $\mathit{legs} = 2$ from Bird (neither Emperor nor Penguin overrides it); $\mathit{height\_cm} = 115$ from Emperor
    (Opus inherits it from his own class); $\mathit{swims} = \mathit{True}$ from Penguin. `lookup` returns
    `(2, 'Bird')`, `(115, 'Emperor')` and `(True, 'Penguin')`.

??? question "3. An interpretation has domain {r1, w1, w2, b}, with Rover = {r1}, Wheel = {w1, w2}, Broken = {w2}, and hasPart = {(r1, w1), (r1, w2), (r1, b)}. Which of r1, w1 belong to ∃hasPart.Wheel, ∀hasPart.Wheel, and ∃hasPart.Broken ⊓ ∀hasPart.¬Rover?"

    $r_1$: it has a wheel part ($w_1$), so $r_1 \in \exists \mathit{hasPart}.\mathit{Wheel}$. Not all its parts are
    wheels ($b$ is not), so $r_1 \notin \forall \mathit{hasPart}.\mathit{Wheel}$. It has a broken part ($w_2$) and no
    part is a rover, so it is in the third concept. $w_1$ has no parts: it is not in $\exists
    \mathit{hasPart}.\mathit{Wheel}$, but it *is* in $\forall \mathit{hasPart}.\mathit{Wheel}$ (vacuously: every one of
    its zero parts is a wheel), and not in the third (no broken part). The vacuous truth of $\forall$ surprises people,
    and is the reason ontologies often write $\exists r.C \sqcap \forall r.C$ ("has some, and only").

??? question "4. Use the tableau rules by hand to show that ∃r.A ⊓ ∃r.B is not subsumed by ∃r.(A ⊓ B), and give the counter-model."

    Test satisfiability of $\exists r.A \sqcap \exists r.B \sqcap \lnot\exists r.(A \sqcap B)$, in NNF $\exists r.A \sqcap
    \exists r.B \sqcap \forall r.(\lnot A \sqcup \lnot B)$. The $\sqcap$-rule puts all three in the root's label. The
    $\exists$-rule makes successor $y_1$ with $\{A\}$ and $y_2$ with $\{B\}$. The $\forall$-rule adds $\lnot A \sqcup
    \lnot B$ to both. At $y_1$, choosing $\lnot A$ clashes, so choose $\lnot B$: label $\{A, \lnot B\}$. At $y_2$,
    $\lnot B$ clashes, so $\lnot A$: $\{B, \lnot A\}$. No clash remains: the concept is satisfiable and the subsumption
    fails. The model has a root with two $r$-successors, one in $A$ only and one in $B$ only. With an empty TBox the
    program's `print_model` shows exactly `--r--> A, ¬B` and `--r--> B, ¬A`.

??? question "5. Write the code: with the TBox {Lake ⊓ Rock ⊑ ⊥}, is ∃formedIn.Lake ⊓ ∀formedIn.Rock satisfiable? And ∃formedIn.Lake ⊓ ∀formedIn.(Rock ⊔ Water)?"

    ```python
    from ch11_tableau import Reasoner, AND

    R = Reasoner([(AND("Lake", "Rock"), "BOTTOM")])
    print(R.satisfiable(AND(("some", "formedIn", "Lake"), ("all", "formedIn", "Rock"))))
    print(R.satisfiable(AND(("some", "formedIn", "Lake"), ("all", "formedIn", ("or", "Rock", "Water")))))
    ```

    It prints `False` and `True`. In the first, the successor must be both a Lake and a Rock, which the TBox forbids. In
    the second, the successor is a Lake, and the disjunction is satisfied by Water (nothing says a lake is not water).

??? question "6. Write the successor-state axiom for Holding(x, s) given actions PickUp(x) and Drop(x). How many axioms would the frame-axiom approach need for 10 actions and 20 fluents?"

    $\mathit{Holding}(x, \mathit{do}(a, s)) \Leftrightarrow a = \mathit{PickUp}(x) \lor (\mathit{Holding}(x, s) \land a
    \neq \mathit{Drop}(x))$. With frame axioms, each pair of an action and a fluent it does not affect needs an axiom
    (sometimes two, for staying true and staying false), so roughly $10 \times 20 = 200$, up to 400; with successor-state
    axioms, 20, one per fluent, each of a size proportional to the number of actions that affect that fluent.

??? question "7. In the event-calculus narrative, add HeaterOff at time 14. Which fluents hold at time 15 and at time 16?"

    The heater switched on at 12 is now terminated at 14, so Heating holds at 13 and 14 but not at 15 or 16 (a fluent
    terminated at $t_1$ is false after $t_1$). At 15 nothing holds: Daylight returns only after the SunRise at 15, so it
    holds at 16. At 16: only Daylight. (Add `(14, "HeaterOff")` to `NARRATIVE` and the table changes in exactly these
    rows.)

??? question "8. Compute by hand the composition meets ∘ during: A meets B and B during C. Then check with the table."

    $A$ ends exactly where $B$ starts, and $B$ lies strictly inside $C$. So $A$ ends strictly inside $C$. Where does $A$
    start? Before $C$ starts (then $A$ overlaps $C$), exactly when $C$ starts (then $A$ starts $C$), or after (then $A$
    is during $C$). So the answer is {overlaps, starts, during}, and `composition_table()[("meets", "during")]` gives
    the same three.

??? question "9. Find all stable models of the program a ← not b; b ← not a; c ← a; c ← b. Is c entailed skeptically?"

    Guess $\{a, c\}$: the rule $b \leftarrow \mathit{not}\; a$ is deleted ($a$ is in the guess); the reduct is $a
    \leftarrow$; $c \leftarrow a$; $c \leftarrow b$, with least model $\{a, c\}$: stable. By symmetry $\{b, c\}$ is
    stable. $\{a, b, c\}$ is not (both choice rules are deleted, the least model is empty), and neither is $\{c\}$ (both
    choice rules survive, the least model is $\{a, b, c\}$). So there are two stable models, both containing $c$: $c$
    holds skeptically, a conclusion reached by cases, although neither $a$ nor $b$ does. `stable_models` returns
    `[['A', 'C'], ['B', 'C']]` with capitalised names.

??? question "10. Write the code: after RDFS inference, find each rover that landed in a crater, with each of its instruments."

    ```python
    from ch11_knowledge_graph import TripleStore, TRIPLES, rdfs_closure

    store = TripleStore(TRIPLES)
    rdfs_closure(store)
    q = [("?r", "type", "Rover"), ("?r", "landedIn", "?c"), ("?c", "type", "Crater"),
         ("?r", "hasInstrument", "?i"), ("?i", "type", "Instrument")]
    print(sorted((b["?r"], b["?i"]) for b in store.query(q)))
    ```

    It prints `[('Curiosity', 'ChemCam'), ('Perseverance', 'SuperCam')]`. The last pattern needs inference: no
    triple says either instrument is an Instrument; RDFS derives it from Spectrometer ⊑ Instrument.

??? question "11. A disease has prior probability 0.2. A test result raises the odds by a likelihood ratio of 4. What is the posterior after one positive test, after two independent positive tests, and after the same test is read twice? What would certainty factors do?"

    Prior odds $0.2 / 0.8 = 0.25$. One test: odds $0.25 \times 4 = 1$, probability $0.5$. Two conditionally independent
    tests: odds $0.25 \times 16 = 4$, probability $0.8$. The same result read twice carries no new information: still
    $0.5$. A certainty-factor system with a rule "positive test gives CF 0.6" fires twice in both of the last two
    situations and reports $0.84$ for each; it cannot tell independent evidence from repeated evidence, because the
    rules do not record how the evidence is related. Bayesian networks ([Chapter 12](12-Probabilistic-Reasoning.md))
    record exactly that.

??? question "12. (Advanced) Why does the tableau algorithm need blocking with a general TBox, but not without one? Why is subset blocking (a node's label contained in an ancestor's) sound for ALC?"

    Without a TBox, each successor's label has smaller role depth than its parent's, so the tree's depth is bounded by
    the role depth of the input. A TBox concept such as $\lnot\mathit{Site} \sqcup \exists
    \mathit{linkedTo}.\mathit{Site}$ is added to *every* node, so role depth no longer decreases, and the
    $\exists$-rule can fire forever. Blocking restores termination: there are at most $2^n$ distinct labels, so on any
    branch some label repeats within $2^n$ steps. It is sound because a blocked node $x$ with $L(x) \subseteq L(y)$ for
    an ancestor $y$ can be given $y$'s successors in the model (redirect $x$'s would-be edges to $y$'s children): every
    $\exists r.C$ in $L(x)$ is also in $L(y)$, so it is satisfied there, and every $\forall r.C$ in $L(x)$ is in $L(y)$,
    so $y$'s children already contain $C$. ALC has no inverse roles or number restrictions, which is why this simple
    form of blocking suffices; richer logics need pairwise blocking.

## What you learned

- An ontology fixes the categories of a domain and their relations: membership versus subclass, disjointness,
  exhaustive decompositions and partitions, part-of; inheritance down the hierarchy is the main cheap inference.
- Semantic networks and frames organise knowledge as graphs and records with defaults; the most specific default
  wins, and incomparable defaults (the Nixon diamond) conflict.
- Description logics give networks a precise semantics; the tableau algorithm decides satisfiability and subsumption
  by trying to build a model, terminates (with blocking for general TBoxes), and is sound and complete; complexity
  ranges from polynomial (EL) to very high (SROIQ, the logic of OWL 2).
- Change and time: successor-state axioms solve the frame problem in the situation calculus with one axiom per
  fluent; the event calculus encodes inertia on a time line; Allen's 13 interval relations support path-consistency
  reasoning.
- Non-monotonic reasoning lets conclusions be withdrawn: the closed world, circumscription (minimal models), default
  logic (extensions, credulous and skeptical), and stable models, which power answer set programming.
- Knowledge graphs are triple stores with indexes, pattern queries, rule inference (RDFS) and learned embeddings
  (TransE); expert systems faded because of the knowledge acquisition bottleneck, brittleness, maintenance, uncertainty
  without semantics and no learning, but their ideas live on in rule engines, ontologies and knowledge graphs.

**Next:** [Chapter 12](12-Probabilistic-Reasoning.md) replaces "true or false" with degrees of belief: probability,
Bayes' rule, Bayesian networks, and exact and approximate inference in them.

## Further reading

- S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed., 2020: chapter 10 (knowledge
  representation).
- R. J. Brachman and H. J. Levesque, *Knowledge Representation and Reasoning*, 2004.
- F. Baader, I. Horrocks, C. Lutz and U. Sattler, *An Introduction to Description Logic*, 2017; F. Baader et al.
  (eds.), *The Description Logic Handbook*, 2nd ed., 2007.
- M. Schmidt-Schauß and G. Smolka, "Attributive concept descriptions with complements", *Artificial Intelligence* 48,
  1991; F. Baader, S. Brandt and C. Lutz, "Pushing the EL envelope", IJCAI 2005.
- M. R. Quillian, "Semantic memory", in M. Minsky (ed.), *Semantic Information Processing*, 1968; M. Minsky, "A
  framework for representing knowledge", MIT AI Laboratory Memo 306, 1974 (published 1975); W. A. Woods, "What's in a
  link: foundations for semantic networks", 1975; R. J. Brachman, "What IS-A is and isn't", *IEEE Computer* 16, 1983;
  R. J. Brachman and J. G. Schmolze, "An overview of the KL-ONE knowledge representation system", *Cognitive Science*
  9, 1985.
- D. S. Touretzky, *The Mathematics of Inheritance Systems*, 1986.
- J. McCarthy and P. J. Hayes, "Some philosophical problems from the standpoint of artificial intelligence", *Machine
  Intelligence* 4, 1969; R. Reiter, *Knowledge in Action: Logical Foundations for Specifying and Implementing Dynamical
  Systems*, 2001.
- R. Kowalski and M. Sergot, "A logic-based calculus of events", *New Generation Computing* 4, 1986; M. Shanahan,
  *Solving the Frame Problem*, 1997.
- J. F. Allen, "Maintaining knowledge about temporal intervals", *Communications of the ACM* 26, 1983; B. Nebel and
  H.-J. Bürckert, "Reasoning about temporal relations: a maximal tractable subclass of Allen's interval algebra",
  *Journal of the ACM* 42, 1995.
- R. Reiter, "On closed world data bases", 1978; R. Reiter, "A logic for default reasoning", *Artificial Intelligence*
  13, 1980; J. McCarthy, "Circumscription: a form of non-monotonic reasoning", *Artificial Intelligence* 13, 1980.
- M. Gelfond and V. Lifschitz, "The stable model semantics for logic programming", ICLP 1988; M. Gebser, R. Kaminski,
  B. Kaufmann and T. Schaub, *Answer Set Solving in Practice*, 2012.
- C. E. Alchourrón, P. Gärdenfors and D. Makinson, "On the logic of theory change: partial meet contraction and
  revision functions", *Journal of Symbolic Logic* 50, 1985.
- A. Bordes, N. Usunier, A. García-Durán, J. Weston and O. Yakhnenko, "Translating embeddings for modeling
  multi-relational data", NeurIPS 2013; A. Hogan et al., "Knowledge graphs", *ACM Computing Surveys* 54, 2021.
- E. H. Shortliffe, *Computer-Based Medical Consultations: MYCIN*, 1976; B. G. Buchanan and E. H. Shortliffe (eds.),
  *Rule-Based Expert Systems*, 1984; V. L. Yu et al., "Antimicrobial selection by a computer: a blinded evaluation by
  infectious diseases experts", *JAMA* 242, 1979; D. Heckerman, "Probabilistic interpretations for MYCIN's certainty
  factors", in *Uncertainty in Artificial Intelligence*, 1986; J. McDermott, "R1: a rule-based configurer of computer
  systems", *Artificial Intelligence* 19, 1982.
- On this site: [Chapter 9](09-First-Order-Logic.md) (first-order logic, Datalog, Prolog), [Chapter 7](07-Constraint-Satisfaction.md)
  (constraint propagation), [Chapter 1](01-What-Is-AI.md) (the history of expert systems), the Machine learning book's
  [Chapter 5](../machine-learning/05-Optimization.md) (gradient descent), and the Logic book's
  [Other logics](https://math.akadian.ca/books/logic/19-Other-Logics.html) at math.akadian.ca.
