# 9. First-order logic and inference

*Propositional logic ([Chapter 8](08-Propositional-Logic-and-SAT.md)) can say "square [1,2] has a pit", but it cannot
say "every square next to a pit is breezy" without writing one sentence per square. The world is made of objects and
the relations between them, and a knowledge base should be able to talk about all of them at once. This chapter answers
the question: what language lets an agent state general rules about objects, and how does a program draw conclusions
from such rules? You will learn first-order logic, its syntax and its meaning, write knowledge in it, build the one
operation every first-order reasoner needs (unification), use it for forward chaining, backward chaining (a small
Prolog) and resolution, and finally meet the hard limits: first-order entailment can be confirmed when it holds, but no
program can always say "no".*

!!! abstract "In this chapter"
    **You will learn:**

    - objects, relations, functions and quantifiers, and why propositional logic cannot say "for every"
    - what a first-order sentence means: models, interpretations, and entailment
    - how to write knowledge in first-order logic, and the two classic quantifier mistakes
    - unification (Robinson 1965): the most general unifier, the occurs check, and a proof that the algorithm is right
    - forward chaining (with a fixed-point guarantee for Datalog) and backward chaining, which is how Prolog runs
    - clausal form with Skolem functions, and resolution with factoring, which is refutation-complete
    - the limits: semi-decidability (Church and Turing, 1936), and why Gödel's completeness theorem does not contradict
      his incompleteness theorem

    **You need:** [Chapter 8](08-Propositional-Logic-and-SAT.md) (propositional syntax, entailment, CNF, resolution,
    Horn clauses). The Logic book's [First-order logic](https://math.akadian.ca/books/logic/10-First-Order-Logic.html)
    chapter is a good second view of 9.1 and 9.2. Section 9.6 uses the idea of a Turing machine and the halting problem
    ([Algorithms, Chapter 1](../algorithms/01-What-Is-an-Algorithm.md)).

    **Levels:** 9.1 and 9.2 are beginner; 9.3 and 9.4 are intermediate; 9.5 is intermediate with an advanced
    completeness sketch; 9.6 is advanced.

## 9.1 Objects, relations, quantifiers; why propositional logic is not enough

Here is a rule a wumpus-world agent ([Chapter 8](08-Propositional-Logic-and-SAT.md)) needs: *a square is breezy exactly
when a neighbouring square has a pit.* In propositional logic every fact is a single symbol, such as $B_{1,1}$ ("square
[1,1] is breezy") or $P_{1,2}$ ("square [1,2] has a pit"), so the rule becomes one sentence per square:

$$
B_{1,1} \Leftrightarrow (P_{1,2} \lor P_{2,1}), \qquad B_{1,2} \Leftrightarrow (P_{1,1} \lor P_{2,2} \lor P_{1,3}), \qquad \ldots
$$

A 4 by 4 cave needs 16 such sentences; a 100 by 100 cave needs 10 000. Worse, the knowledge base never states the
rule itself. It states 10 000 separate facts that happen to look alike, and nothing in the logic knows they are the same
idea. Ask it about a 101st column and it has nothing to say.

The fix is to look at what the sentences are about. The world contains **objects** (squares, pits, the agent, the
number 3), and objects have **properties** and stand in **relations** to one another (square [1,2] is *adjacent to*
square [1,1]; the agent is *at* [1,1]). Some relations are so tidy that each input has exactly one output; we call
those **functions** (the square *to the left of* [2,1] is [1,1]; the *mother of* Ada is one particular person). Natural
language is built on exactly these pieces: nouns name objects, adjectives and verbs name properties and relations, and
words like "every" and "some" say how many objects a statement is about.

**First-order logic** (FOL, also called *predicate logic* or *first-order predicate calculus*) is the logic of objects,
relations, functions and the two words "every" and "some". With it, the breeze rule is one sentence:

$$
\forall s \; \big(\mathit{Breezy}(s) \Leftrightarrow \exists r \; (\mathit{Adjacent}(r, s) \land \mathit{Pit}(r))\big).
$$

Read it aloud: "for every square $s$, $s$ is breezy if and only if there exists a square $r$ that is adjacent to $s$
and has a pit." The symbol $\forall$ (an upside-down A, for "all") is the **universal quantifier**; $\exists$ (a
backwards E, for "exists") is the **existential quantifier**. The letters $s$ and $r$ are **variables**: placeholders
that range over all the objects in the world.

What did we gain? The sentence is short, it is independent of the size of the cave, and it applies to squares the
agent has never seen. That is the jump from a lookup table to a law.

Why "first-order"? Because the variables range over *objects* only. A logic in which variables can also range over
relations ("for every property $P$, ...") is called *second-order*. Second-order logic is more expressive, but, as
9.6 explains, it gives up the property that makes FOL so useful for machines: a complete proof procedure.

Russell and Norvig describe the difference between logics by their **ontological commitment** (what the logic assumes
exists) and their **epistemological commitment** (what an agent can believe about each sentence). Propositional logic
assumes the world consists of facts; first-order logic assumes it consists of objects with relations. Both let a
sentence be believed true, believed false, or unknown. Probability theory ([Chapter 12](12-Probabilistic-Reasoning.md))
keeps the facts but changes the epistemology to degrees of belief between 0 and 1.

## 9.2 Writing knowledge in first-order logic

### Syntax: the pieces

A first-order language starts from a **vocabulary** (also called a *signature*): a set of names, each of a fixed
kind and **arity** (number of arguments).

- **Constant symbols** name objects: `Ada`, `Jezero`, `Zero`. This chapter writes them with a capital letter.
- **Predicate symbols** name relations, with an arity: `Rover` (arity 1, a property), `Has` (arity 2),
  `Between` (arity 3).
- **Function symbols** name functions, with an arity: `Mother` (arity 1), `Plus` (arity 2).
- **Variables** are lower-case letters: $x$, $y$, $s$.

From these we build two kinds of expressions. A **term** names an object: a constant, a variable, or a function applied
to terms, such as `Mother(Ada)` or `Plus(x, S(Zero))`. A term with no variables is a **ground term**. A **formula** says
something:

- an **atomic sentence** (atom) is a predicate applied to terms, $\mathit{Has}(\mathit{Percy}, \mathit{Mother}(x))$,
  or an equality $t_1 = t_2$ between two terms;
- if $\alpha$ and $\beta$ are formulas, so are $\lnot \alpha$, $\alpha \land \beta$, $\alpha \lor \beta$,
  $\alpha \Rightarrow \beta$ and $\alpha \Leftrightarrow \beta$, exactly as in propositional logic;
- if $\alpha$ is a formula and $x$ a variable, $\forall x\, \alpha$ and $\exists x\, \alpha$ are formulas.

A variable inside $\forall x\, \alpha$ or $\exists x\, \alpha$ is **bound** by that quantifier; one that is not bound
is **free**. A formula with no free variables is a **sentence**; only sentences are true or false on their own. When a
knowledge base contains a formula with free variables, such as `Parent(x, y) & Parent(y, z) => Grandparent(x, z)`, the
convention is that the variables are universally quantified at the front.

### Semantics: what a sentence means

Symbols mean nothing until we say what they refer to. A **model** (also called a *structure* or *interpretation*) for a
vocabulary consists of:

1. a nonempty set $D$, the **domain** (the objects that exist in this possible world);
2. for each constant symbol, an object of $D$;
3. for each predicate symbol of arity $k$, a set of $k$-tuples of objects (the tuples for which the relation holds);
4. for each function symbol of arity $k$, a total function from $D^k$ to $D$ (every input has an output, possibly a
   dull one).

Figure 9.1 draws a small model.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 260" role="img" aria-label="A model with four objects: a rover, a camera, a second camera and a crater. Arrows show the relation Has from the rover to the first camera, At from the rover to the crater, and the function CameraOf mapping the rover to the first camera. Labels show which objects satisfy the unary predicates Rover, Camera and Crater.">
<rect x="10" y="10" width="620" height="210" rx="14" fill="none" stroke="currentColor" stroke-width="1.2" stroke-dasharray="6 4"/>
<text x="24" y="32" font-size="13" fill="currentColor">domain D</text>
<circle cx="120" cy="120" r="34" fill="#eea66f" fill-opacity="0.35" stroke="currentColor" stroke-width="1.4"/>
<text x="120" y="117" font-size="13" text-anchor="middle" fill="currentColor">object 1</text>
<text x="120" y="133" font-size="12" text-anchor="middle" fill="currentColor">Rover</text>
<circle cx="330" cy="70" r="34" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1.4"/>
<text x="330" y="67" font-size="13" text-anchor="middle" fill="currentColor">object 2</text>
<text x="330" y="83" font-size="12" text-anchor="middle" fill="currentColor">Camera</text>
<circle cx="520" cy="80" r="34" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1.4"/>
<text x="520" y="77" font-size="13" text-anchor="middle" fill="currentColor">object 3</text>
<text x="520" y="93" font-size="12" text-anchor="middle" fill="currentColor">Camera</text>
<circle cx="380" cy="172" r="34" fill="#7ccf9a" fill-opacity="0.45" stroke="currentColor" stroke-width="1.4"/>
<text x="380" y="169" font-size="13" text-anchor="middle" fill="currentColor">object 4</text>
<text x="380" y="185" font-size="12" text-anchor="middle" fill="currentColor">Crater</text>
<path d="M152,106 Q230,70 296,72" fill="none" stroke="currentColor" stroke-width="1.5"/>
<polygon points="296,72 286,67 287,77" fill="currentColor"/>
<text x="222" y="72" font-size="13" text-anchor="middle" fill="currentColor">Has</text>
<path d="M152,134 Q250,175 346,174" fill="none" stroke="currentColor" stroke-width="1.5"/>
<polygon points="346,174 336,169 336,179" fill="currentColor"/>
<text x="246" y="176" font-size="13" text-anchor="middle" fill="currentColor">At</text>
<path d="M140,92 Q230,20 300,52" fill="none" stroke="#eea66f" stroke-width="2" stroke-dasharray="5 3"/>
<polygon points="300,52 293,44 289,53" fill="#eea66f"/>
<text x="200" y="42" font-size="13" text-anchor="middle" fill="currentColor">CameraOf(·)</text>
<text x="24" y="246" font-size="13" fill="currentColor">Percy ↦ object 1,  Jezero ↦ object 4.  True here: Has(Percy, CameraOf(Percy)),  ∃y (Camera(y) ∧ ¬Has(Percy, y)).</text>
</svg>
<figcaption>Figure 9.1. A model. The domain has four objects; the constant Percy refers to object 1 and Jezero to object 4;
the relation Has holds for one pair, At for another; the function CameraOf maps object 1 to object 2 (and, to be total,
must map every other object somewhere too, not drawn). A sentence is true or false in a model like this one.</figcaption>
</figure>

Truth is then defined by working inward through the sentence:

- An atom $P(t_1, \ldots, t_k)$ is true when the tuple of objects named by $t_1, \ldots, t_k$ is in the set for $P$.
  An equality $t_1 = t_2$ is true when both terms name the same object.
- The connectives work exactly as in propositional logic.
- $\forall x\, \alpha$ is true when $\alpha$ is true for *every* way of letting $x$ stand for an object of $D$.
- $\exists x\, \alpha$ is true when $\alpha$ is true for *at least one* way of letting $x$ stand for an object of $D$.

**Entailment** is defined just as before: $\mathit{KB} \models \alpha$ ("KB entails $\alpha$") when $\alpha$ is true in
every model in which all of $\mathit{KB}$ is true. A sentence true in every model is **valid**; one true in some model
is **satisfiable**. And the key fact from [Chapter 8](08-Propositional-Logic-and-SAT.md) survives unchanged:

$$
\mathit{KB} \models \alpha \quad \text{if and only if} \quad \mathit{KB} \land \lnot\alpha \text{ is unsatisfiable.}
$$

There is a new difficulty. A propositional knowledge base with $n$ symbols has $2^n$ models, and a truth table can list
them all. A first-order knowledge base has infinitely many models: the domain can have any size, including infinite,
and the constants can be mapped in any way. Model checking by enumeration is impossible, so first-order reasoning must
be done by **inference rules** that manipulate sentences. The rest of the chapter builds them.

### Quantifiers in practice

Quantifiers obey a few laws that you will use constantly:

- **Negation flips them** (De Morgan's laws for quantifiers): $\lnot \forall x\, P(x) \equiv \exists x\, \lnot P(x)$
  ("not everyone is happy" is "someone is unhappy"), and $\lnot \exists x\, P(x) \equiv \forall x\, \lnot P(x)$.
- **Like quantifiers commute**: $\forall x \forall y$ is the same as $\forall y \forall x$; the same for $\exists$.
- **Unlike quantifiers do not.** $\forall x \exists y\, \mathit{Loves}(x, y)$, "everybody loves somebody", allows
  everyone to love a different person. $\exists y \forall x\, \mathit{Loves}(x, y)$, "there is somebody whom everybody
  loves", says one person is loved by all. The second entails the first, but not the other way.

### Two classic mistakes

The natural partner of $\forall$ is $\Rightarrow$, and the natural partner of $\exists$ is $\land$. Mixing them up is
the commonest error in writing first-order logic.

*"All rovers have wheels."* The right sentence is $\forall x\, (\mathit{Rover}(x) \Rightarrow \mathit{HasWheels}(x))$.
The wrong one, $\forall x\, (\mathit{Rover}(x) \land \mathit{HasWheels}(x))$, says *everything* is a rover with wheels,
including the crater and the number 3.

*"Some rover has a drill."* The right sentence is $\exists x\, (\mathit{Rover}(x) \land \mathit{HasDrill}(x))$. The
wrong one, $\exists x\, (\mathit{Rover}(x) \Rightarrow \mathit{HasDrill}(x))$, is true as soon as there is any object
that is *not* a rover (for that object the implication is vacuously true), so it says almost nothing.

### A small knowledge base, written properly

**Knowledge engineering** is the craft of writing a knowledge base. The usual steps are: decide what questions it must
answer; collect the relevant knowledge; choose a vocabulary (which predicates, functions and constants); write general
axioms; write the specific facts of the problem; pose queries; and debug. Debugging a knowledge base is like debugging
a program, except that the bug is usually a *missing* axiom, or one that says less than you meant.

Here is a family vocabulary: the predicate $\mathit{Parent}(x, y)$, "$x$ is a parent of $y$", and derived relations
defined from it.

$$
\begin{aligned}
&\forall x\, \forall z\; \big(\mathit{Grandparent}(x, z) \Leftrightarrow \exists y\, (\mathit{Parent}(x, y) \land \mathit{Parent}(y, z))\big) \\
&\forall x\, \forall y\; \big(\mathit{Sibling}(x, y) \Leftrightarrow x \neq y \land \exists p\, (\mathit{Parent}(p, x) \land \mathit{Parent}(p, y))\big) \\
&\forall x\, \forall z\; \big(\mathit{Ancestor}(x, z) \Leftrightarrow \mathit{Parent}(x, z) \lor \exists y\, (\mathit{Parent}(x, y) \land \mathit{Ancestor}(y, z))\big)
\end{aligned}
$$

Notice the $x \neq y$ in $\mathit{Sibling}$: without it, everyone with a parent is their own sibling. That is the kind of
bug knowledge engineers hunt for. Notice also that the $\mathit{Ancestor}$ definition is recursive; first-order logic
has no trouble with that, but, as 9.6 shows, the biconditional does not quite pin down the *least* such relation, and
programs that reason with it normally use only the "if" direction. The code in 9.4 runs exactly these rules.

Arithmetic is the most famous example. With a constant $0$, a one-place function $S$ ("successor", so $S(0)$ means 1)
and a predicate $\mathit{Nat}$:

$$
\mathit{Nat}(0), \qquad \forall n\, (\mathit{Nat}(n) \Rightarrow \mathit{Nat}(S(n))), \qquad \forall m\, (\mathit{Plus}(0, m) = m), \qquad \forall m\, \forall n\, (\mathit{Plus}(S(m), n) = S(\mathit{Plus}(m, n))).
$$

These are the start of the Peano axioms (Giuseppe Peano, 1889). Function symbols make terms of unbounded depth,
$S(S(S(0)))$ and so on, and that is the source of both FOL's power and its undecidability.

**Equality** deserves one sentence of warning. Different constants may name the same object: $\mathit{Mother}(Ben) =
Ada$ is a real statement. Logic does not assume that different names mean different things (the **unique names
assumption**) or that the listed objects are all there is (the **domain closure assumption**). Databases and Prolog do
make both assumptions, as part of their **closed-world** reading of facts; [Chapter 11](11-Knowledge-Representation.md)
returns to this.

## 9.3 Unification (Robinson 1965) from scratch

*Level: intermediate.*

### The problem

Suppose the knowledge base contains the rule and the fact

$$
\forall x\, \forall y\; \big(\mathit{Camera}(y) \land \mathit{Has}(x, y) \Rightarrow \mathit{CanSee}(x)\big), \qquad \mathit{Has}(\mathit{Percy}, \mathit{Navcam}), \qquad \mathit{Camera}(\mathit{Navcam}).
$$

Obviously $\mathit{CanSee}(\mathit{Percy})$ follows. One way to see it is **universal instantiation**: from
$\forall x\, \alpha$ we may conclude $\alpha$ with any ground term substituted for $x$. Substitute $\mathit{Percy}$ for
$x$ and $\mathit{Navcam}$ for $y$, and the rule becomes a propositional implication; ordinary modus ponens finishes.

The first first-order provers worked exactly this way. They **propositionalized** the knowledge base: replace every
universally quantified sentence by all its ground instances, then run a propositional method. Herbrand's theorem
(Jacques Herbrand, 1930) says this is complete: if $\mathit{KB} \models \alpha$, then some *finite* set of ground
instances already entails it. But with function symbols the set of ground terms is infinite ($\mathit{Percy}$,
$\mathit{Mother}(\mathit{Percy})$, $\mathit{Mother}(\mathit{Mother}(\mathit{Percy}))$, ...), and even without them the
number of instances of a rule with $k$ variables over $n$ constants is $n^k$. Programs of the early 1960s (Gilmore 1960;
Davis and Putnam 1960) drowned in instances.

The better idea is to instantiate *only as much as needed, only when needed*. To use the rule above, we need its premise
$\mathit{Has}(x, y)$ to match the fact $\mathit{Has}(\mathit{Percy}, \mathit{Navcam})$. So ask: *what substitution
for the variables makes these two expressions identical?* Here, $\{x/\mathit{Percy}, y/\mathit{Navcam}\}$. Finding
that substitution is **unification**, and it is the one primitive operation of first-order inference.

### Substitutions and unifiers

A **substitution** $\theta$ is a finite set of bindings $\{x_1/t_1, \ldots, x_n/t_n\}$, each replacing a variable by a
term. Applying $\theta$ to an expression $e$, written $e\theta$ (or $\mathrm{SUBST}(\theta, e)$), replaces every
occurrence of each $x_i$ by $t_i$. A **unifier** of two expressions $p$ and $q$ is a substitution with $p\theta =
q\theta$.

Unifiers are not unique. $\mathit{Knows}(\mathit{John}, x)$ and $\mathit{Knows}(y, z)$ are unified by
$\{y/\mathit{John}, x/z\}$, and also by $\{y/\mathit{John}, x/\mathit{Bill}, z/\mathit{Bill}\}$. The second one commits
to more than necessary: it picks Bill for no reason. Every unifier of these two is the first one followed by some
further substitution. That makes the first one a **most general unifier (MGU)**: a unifier $\sigma$ such that for every
unifier $\theta$ there is a substitution $\lambda$ with $\theta = \sigma\lambda$ (apply $\sigma$, then $\lambda$).

**Theorem (Robinson 1965).** If two expressions have a unifier, they have a most general unifier, and it is unique up to
renaming variables. The algorithm below computes it or reports that none exists.

### The algorithm

Keep a list of equations still to solve, starting with $p = q$, and a substitution $\theta$, starting empty. Repeatedly
take an equation $a = b$, first replacing any bound variable in $a$ or $b$ by what it is bound to, and:

1. **Delete.** If $a$ and $b$ are identical, drop the equation.
2. **Bind.** If one side is a variable $v$ and the other a term $t$: if $v$ occurs inside $t$, **fail** (the
   *occurs check*); otherwise add $v/t$ to $\theta$.
3. **Decompose.** If both are compound with the same function or predicate symbol and the same number of arguments,
   $f(a_1, \ldots, a_k) = f(b_1, \ldots, b_k)$, replace the equation by the $k$ equations $a_i = b_i$.
4. **Clash.** Otherwise (two different constants, two different function symbols, a constant against a compound term)
   **fail**.

When the list is empty, $\theta$ is the MGU. Here is the program's trace for $\mathit{Knows}(\mathit{John}, x,
\mathit{Mother}(x))$ against $\mathit{Knows}(y, \mathit{Jane}, z)$:

| step | equation solved | rule | $\theta$ afterwards |
|---|---|---|---|
| 1 | Knows(John, x, Mother(x)) = Knows(y, Jane, z) | decompose | {} |
| 2 | John = y | bind | {y/John} |
| 3 | x = Jane | bind | {y/John, x/Jane} |
| 4 | Mother(x) = z | bind | {y/John, x/Jane, z/Mother(x)} |

Written in *solved form* (every right side fully substituted), the answer is $\{y/\mathit{John}, x/\mathit{Jane},
z/\mathit{Mother}(\mathit{Jane})\}$. Figure 9.2 shows the same thing as matching two trees.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 230" role="img" aria-label="Two term trees side by side. Left: Knows with children John, x and Mother(x). Right: Knows with children y, Jane and z. Dashed lines connect the positions that unification matches: John with y, x with Jane, Mother(x) with z.">
<rect x="105" y="20" width="90" height="30" rx="6" fill="#eea66f" fill-opacity="0.35" stroke="currentColor"/>
<text x="150" y="40" font-size="13" text-anchor="middle" fill="currentColor">Knows</text>
<line x1="130" y1="50" x2="60" y2="100" stroke="currentColor"/>
<line x1="150" y1="50" x2="150" y2="100" stroke="currentColor"/>
<line x1="170" y1="50" x2="240" y2="100" stroke="currentColor"/>
<rect x="25" y="100" width="70" height="28" rx="6" fill="none" stroke="currentColor"/>
<text x="60" y="119" font-size="13" text-anchor="middle" fill="currentColor">John</text>
<circle cx="150" cy="114" r="15" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/>
<text x="150" y="119" font-size="13" text-anchor="middle" fill="currentColor">x</text>
<rect x="205" y="100" width="70" height="28" rx="6" fill="none" stroke="currentColor"/>
<text x="240" y="119" font-size="13" text-anchor="middle" fill="currentColor">Mother</text>
<line x1="240" y1="128" x2="240" y2="160" stroke="currentColor"/>
<circle cx="240" cy="175" r="15" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/>
<text x="240" y="180" font-size="13" text-anchor="middle" fill="currentColor">x</text>
<rect x="445" y="20" width="90" height="30" rx="6" fill="#eea66f" fill-opacity="0.35" stroke="currentColor"/>
<text x="490" y="40" font-size="13" text-anchor="middle" fill="currentColor">Knows</text>
<line x1="470" y1="50" x2="400" y2="100" stroke="currentColor"/>
<line x1="490" y1="50" x2="490" y2="100" stroke="currentColor"/>
<line x1="510" y1="50" x2="580" y2="100" stroke="currentColor"/>
<circle cx="400" cy="114" r="15" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/>
<text x="400" y="119" font-size="13" text-anchor="middle" fill="currentColor">y</text>
<rect x="455" y="100" width="70" height="28" rx="6" fill="none" stroke="currentColor"/>
<text x="490" y="119" font-size="13" text-anchor="middle" fill="currentColor">Jane</text>
<circle cx="580" cy="114" r="15" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/>
<text x="580" y="119" font-size="13" text-anchor="middle" fill="currentColor">z</text>
<path d="M60,128 Q230,215 400,129" fill="none" stroke="#7ccf9a" stroke-width="2" stroke-dasharray="6 3"/>
<path d="M150,129 Q320,200 490,128" fill="none" stroke="#7ccf9a" stroke-width="2" stroke-dasharray="6 3"/>
<path d="M275,114 Q430,80 565,114" fill="none" stroke="#7ccf9a" stroke-width="2" stroke-dasharray="6 3"/>
<text x="320" y="222" font-size="13" text-anchor="middle" fill="currentColor">MGU: y/John, x/Jane, z/Mother(Jane)</text>
</svg>
<figcaption>Figure 9.2. Unification matches two term trees position by position. Same symbols at the top let us
decompose; a variable (blue circle) may be bound to whatever sits opposite it. The binding of x to Jane then flows into
the subterm Mother(x) that z was bound to.</figcaption>
</figure>

The program [`ch09_unify.py`](#the-unification-program) implements exactly the four rules, with terms as Python
tuples and variables as strings starting with `?`.

### Why it is correct

**Theorem.** The algorithm always halts. If it returns $\theta$, then $\theta$ is a most general unifier; if it fails,
no unifier exists.

*Termination.* Measure the state by the pair (number of distinct variables that are still unbound and appear in the
equation list, total number of symbols in the equation list), compared lexicographically (first entry first). *Bind*
removes a variable from the list for good: it is replaced everywhere it is later met by its binding, and the occurs
check guarantees that the binding does not contain it, so the first entry drops. *Delete* and *Decompose* never add a
variable, and they shrink the second entry (decompose removes the two function symbols). Every step lowers the measure,
and a lexicographic order on pairs of natural numbers has no infinite descending chain, so the algorithm halts.

*Correctness.* The key invariant: **at every step, the set of unifiers of (equations left, plus bindings in $\theta$)
is the same as the set of unifiers of the original pair.** Check each rule. Delete removes an equation every
substitution satisfies. Decompose is valid because $f(a_1..a_k)\lambda = f(b_1..b_k)\lambda$ holds exactly when
every $a_i\lambda = b_i\lambda$. Bind: a substitution $\lambda$ satisfies $v = t$ exactly when $v\lambda = t\lambda$,
which is exactly when $\lambda$ agrees with "first replace $v$ by $t$, then apply $\lambda$"; so recording $v/t$ loses
no unifier and admits no false one. Failure is justified too: a clash $f(\ldots) = g(\ldots)$ cannot be fixed by any
substitution (substitution never changes the top symbol of a compound term or a constant), and $v = t$ with $v$ inside
a compound $t$ cannot either, because $t\lambda$ would contain $v\lambda$ as a proper part and so be strictly larger.

*Most general.* Let $\lambda$ be any unifier of the original pair. By the invariant, $\lambda$ satisfies every binding
$v/t$ that was recorded: $v\lambda = t\lambda$. Following the chain of bindings (by induction on its length), applying
$\theta$ first and $\lambda$ afterwards gives the same result as $\lambda$ alone, on every variable; that is,
$\lambda = \theta\lambda$. So every unifier is an instance of $\theta$. $\square$

The program checks this claim on one case: the MGU of $\mathit{Knows}(y, x)$ and $\mathit{Knows}(z,
\mathit{Mother}(y))$ is $\{y/z, x/\mathit{Mother}(z)\}$, and the more specific unifier $\{y/\mathit{John},
x/\mathit{Mother}(\mathit{John}), z/\mathit{John}\}$ is that MGU followed by $\{z/\mathit{John}\}$.

### The occurs check, and the cost

The occurs check stops $x = f(x)$ from "succeeding" with an infinite term. Without it, unifying $P(x, f(x))$ with
$P(y, y)$ produces the bindings $\{x/y, y/f(x)\}$, a cycle: $y = f(y) = f(f(y)) = \cdots$. A prover that accepts this
can "prove" false things. Most Prolog systems leave the check out anyway, because it costs time on every binding and
real programs rarely trigger it; ISO Prolog provides a separate `unify_with_occurs_check/2` for when you need it.

How long does unification take? The answer depends on how terms are stored. Consider

$$
P(x_1, x_2, \ldots, x_n) \quad = \quad P\big(f(x_0, x_0), f(x_1, x_1), \ldots, f(x_{n-1}, x_{n-1})\big).
$$

The MGU binds $x_1$ to $f(x_0, x_0)$, $x_2$ to $f(x_1, x_1)$, and so on, so written out in full $x_n$ is a complete
binary tree with $2^{n+1} - 1$ symbols. Any algorithm that prints the solved form must take exponential time. But the
*triangular* form ($x_2/f(x_1, x_1)$ with $x_1$ left as a pointer) has only $n$ bindings, and the algorithm only needs
$n + 1$ steps to find it, if it never copies terms and never searches the same shared subterm twice. The program
measures this:

```
  n  pairs solved  printed size of x_n
   2             3             7
   4             5            31
   8             9           511
  16            17       131,071
  24            25    33,554,431
```

Getting the occurs check right matters here. The first version of the program searched every subterm on every check;
on $n = 24$ that took tens of seconds, because the shared tree was searched as if it were $2^{25}$ separate nodes. The
fix is to remember which variables have already been searched (the `seen` set in `occurs`). With shared term graphs,
Paterson and Wegman (1978) gave a unification algorithm that runs in time linear in the size of the inputs, and
Martelli and Montanari (1982) gave a nearly linear one that is easier to implement. Textbook implementations, like ours,
are quadratic in the worst case and fast in practice.

### Standardizing apart

One more detail. $\mathit{Knows}(\mathit{John}, x)$ and $\mathit{Knows}(x, \mathit{Elizabeth})$ do not unify ($x$ cannot
be both John and Elizabeth). But if the first is a query, "whom does John know?", and the second is a fact, "everyone
knows Elizabeth", the answer should obviously be Elizabeth. The two $x$'s are different variables that happen to share
a name, since each sentence's variables are quantified separately. So before unifying two sentences, rename the
variables of one of them: $\mathit{Knows}(z, \mathit{Elizabeth})$ unifies with $\mathit{Knows}(\mathit{John}, x)$ by
$\{z/\mathit{John}, x/\mathit{Elizabeth}\}$. This renaming is called **standardizing apart**, and every program in this
chapter does it.

### The unification program

```python
--8<-- "books/ai/ch09_unify.py"
```

```
1. A traced unification
unify Knows(John, x, Mother(x)) with Knows(y, Jane, z)
  solve Knows(John, x, Mother(x)) = Knows(y, Jane, z)
  solve John = y
  bind y -> John
  solve x = Jane
  bind x -> Jane
  solve Mother(x) = z
  bind z -> Mother(x)
result {y/John, x/Jane, z/Mother(Jane)}

2. Examples
  Knows(John, x)         Knows(John, Jane)      {x/Jane}
  Knows(John, x)         Knows(y, Bill)         {y/John, x/Bill}
  Knows(John, x)         Knows(y, Mother(y))    {y/John, x/Mother(John)}
  Knows(John, x)         Knows(x, Elizabeth)    fail
  Knows(John, x)         Knows(z, Elizabeth)    {z/John, x/Elizabeth}
  P(x, x)                P(f(y), f(A))          {x/f(A), y/A}
  P(x, f(x))             P(y, y)                fail
  P(f(x), g(y))          P(f(g(z)), z)          {x/g(g(y)), z/g(y)}
  Q(x, y, z)             Q(y, z, A)             {x/A, y/A, z/A}
  Q(A, B)                Q(x, x)                fail

3. Check: applying each unifier makes both sides identical
  7 unifiers checked
  without the occurs check, P(x, f(x)) = P(y, y) 'succeeds' with {x/y, y/f(x)} (a cyclic binding: y = f(y))
  MGU of Knows(y, x) and Knows(z, Mother(y)): {y/z, x/Mother(z)}
  another unifier {y/John, x/Mother(John), z/John} = MGU followed by {z/John}: True

4. Exponential output, small work
  n  pairs solved  printed size of x_n
   2             3             7
   4             5            31
   8             9           511
  16            17       131,071
  24            25    33,554,431
```

Two rows of the example table are worth tracing by hand. In $P(x, x) = P(f(y), f(A))$ the first equation binds $x$ to
$f(y)$; the second equation is then $f(y) = f(A)$ (after following $x$'s binding), which decomposes to $y = A$. In
$P(f(x), g(y)) = P(f(g(z)), z)$ the first argument gives $x = g(z)$ and the second gives $g(y) = z$, so $z$ becomes
$g(y)$ and, in solved form, $x$ becomes $g(g(y))$.

### Indexing

A knowledge base with a million facts cannot try unification against every fact for every goal. Real systems store
facts in an **index**: at the simplest, a table from each predicate symbol to its facts (**predicate indexing**, which
the backward chainer below does by skipping clauses with the wrong head symbol); better, a hash on the predicate plus
the first argument, as most Prolog systems do; best for theorem provers, **term indexing** structures such as
discrimination trees, which find all stored terms that could unify with a query term without trying each one. This is
the same idea as a database index, and the same trade-off: faster queries, slower inserts, more memory.

## 9.4 Forward chaining, backward chaining; logic programming and Prolog (1972)

*Level: intermediate.*

### Generalized modus ponens

In propositional logic, modus ponens takes $p$ and $p \Rightarrow q$ and concludes $q$. With unification it lifts to
first-order logic in one step. **Generalized modus ponens (GMP)**: from atoms $p_1', \ldots, p_n'$ and a rule
$p_1 \land \cdots \land p_n \Rightarrow q$, if there is a substitution $\theta$ with $p_i'\theta = p_i\theta$ for every
$i$, conclude $q\theta$.

For example, from $\mathit{Parent}(\mathit{Ada}, \mathit{Ben})$, $\mathit{Parent}(\mathit{Ben}, \mathit{Dan})$ and
$\mathit{Parent}(x, y) \land \mathit{Parent}(y, z) \Rightarrow \mathit{Grandparent}(x, z)$, the substitution
$\theta = \{x/\mathit{Ada}, y/\mathit{Ben}, z/\mathit{Dan}\}$ gives $\mathit{Grandparent}(\mathit{Ada},
\mathit{Dan})$.

*GMP is sound.* The rule is universally quantified, so by universal instantiation its instance
$p_1\theta \land \cdots \land p_n\theta \Rightarrow q\theta$ is entailed. Each fact $p_i'$ is universally quantified
too (if it has variables), so $p_i'\theta$ is entailed, and it equals $p_i\theta$. Propositional modus ponens on the
instances gives $q\theta$. $\square$

GMP works on **first-order definite clauses**: disjunctions of literals with *exactly one* positive literal, written as
either an atom (a fact, such as $\mathit{Parent}(\mathit{Ada}, \mathit{Ben})$) or an implication whose premise is a
conjunction of atoms and whose conclusion is one atom. These are the first-order version of the Horn clauses of
[Chapter 8](08-Propositional-Logic-and-SAT.md). Not everything can be written this way: "every rover has *a* camera"
needs an existential, and "Ben or Cleo did it" needs a disjunction of two positive atoms. But a remarkable amount of
practical knowledge can, and inference with definite clauses is much simpler than full resolution.

### Forward chaining

**Forward chaining** starts from the known facts and applies every rule whose premises are satisfied, adding the
conclusions as new facts, and repeats until nothing new appears (a **fixed point**) or the query has been derived. It
is data-driven: it computes consequences whether or not anyone asked for them.

```text
function FORWARD-CHAIN(facts, rules):
    new = facts
    repeat:
        added = {}
        for each rule p1 ∧ ... ∧ pn ⇒ q:
            for each θ that makes every pi equal to some known fact, using at least one fact from new:
                if qθ is not already known: add qθ to added
        if added is empty: return facts           # fixed point
        facts = facts ∪ added;  new = added
```

The phrase "using at least one fact from `new`" is **semi-naive evaluation**: a match made only of old facts was already
tried in an earlier round, so skip it. It changes nothing about the result and saves most of the work.

Here is the program on a family of six people with four rules (direct ancestor, recursive ancestor, grandparent,
sibling). Each round lists the facts it added:

```
1. Forward chaining on a family tree
  round 1: +10  Ancestor(Ada, Ben), Ancestor(Ada, Cleo), Ancestor(Ben, Dan), Ancestor(Cleo, Eve), Ancestor(Dan, Finn), Grandparent(Ada, Dan) ...
  round 2: +3  Ancestor(Ada, Dan), Ancestor(Ada, Eve), Ancestor(Ben, Finn)
  round 3: +1  Ancestor(Ada, Finn)
  fixed point after 3 rounds: 35 facts -> 49 facts
   Ancestor(Ada, Ben), Ancestor(Ada, Cleo), Ancestor(Ada, Dan), Ancestor(Ada, Eve), Ancestor(Ada, Finn)
```

Round 1 adds the 5 direct ancestors, the 3 grandparents and the 2 sibling facts (Ben and Cleo, both ways). Round 2 uses
the new ancestor facts to reach two generations down; round 3, three; round 4 adds nothing, so the program stops. (The
35 starting facts are the 5 parent links plus 30 facts $\mathit{Different}(a, b)$ for the $6 \cdot 5$ ordered pairs of
distinct people, which the sibling rule needs because definite clauses cannot say $x \neq y$.)

### Why it stops, and what it costs: Datalog

A definite-clause knowledge base with **no function symbols** is called a **Datalog** program. Datalog is the language
of deductive databases, and forward chaining on it always terminates.

**Theorem.** Let a Datalog program have $p$ predicates, each of arity at most $k$, and $n$ constants. Forward chaining
reaches a fixed point after at most $p\,n^k$ rounds, and the fixed point contains exactly the atoms entailed by the
program.

*Proof.* Without function symbols, every derived atom is a predicate applied to constants (Datalog rules are required to be
*safe*: every variable of the conclusion also appears in a premise, so it is bound to a constant when the premises
match ground facts), so there are at most $p\,n^k$ possible atoms. Every
round that does not stop adds at least one new atom, so there are at most $p\,n^k$ rounds. *Soundness:* every added atom
is derived by GMP, which is sound. *Completeness:* at the fixed point, define a model $M$ whose domain is the constants
and in which exactly the derived atoms are true. Every rule is true in $M$: if its premises are true in $M$ under some
substitution, they are derived atoms, so the rule fired and its conclusion is derived, hence true. So $M$ is a model of
the knowledge base. If an atom $\alpha$ is entailed, it is true in every model, in particular in $M$, so it was derived.
$\square$

In the family program, $p = 5$, $k = 2$ and $n = 6$ give a bound of 180 possible atoms; it found 49. In a chain of $n$
people with only the ancestor rules, round $r$ adds the ancestor pairs $r$ generations apart, so there are exactly
$n - 1$ productive rounds and $n(n-1)/2$ ancestor facts (Exercise 7 checks this).

How much work is a round? Matching one rule with $m$ premises against $F$ facts by trying all combinations costs up to
$F^m$ unifications, so for a *fixed* program the total is polynomial in the number of facts; database people call this
**data complexity** and it is the reason Datalog is used for program analysis and network configuration checks, where
the facts number in the millions and the rules in the dozens. Matching the premises of one rule is a join of tables, and
choosing a good order for the premises is the database problem of join ordering. In the other direction, with the
program as part of the input, matching even a single rule is NP-hard in general, because finding a substitution that
satisfies a conjunction of premises is a constraint satisfaction problem ([Chapter 7](07-Constraint-Satisfaction.md)).

The **Rete** algorithm (Charles Forgy, 1982) speeds up forward chaining in production systems by compiling the rules
into a network that remembers partial matches between rounds, so that a new fact only extends the matches it touches.
It powered the OPS5 language and many rule-based expert systems ([Chapter 11](11-Knowledge-Representation.md)).

### With function symbols, no fixed point

Add one function symbol and termination is gone:

```
2. A function symbol: no fixed point
  round 1: +1  Nat(S(Zero))
  round 2: +1  Nat(S(S(Zero)))
  round 3: +1  Nat(S(S(S(Zero))))
  round 4: +1  Nat(S(S(S(S(Zero)))))
  round 5: +1  Nat(S(S(S(S(S(Zero))))))
  stopped by the round limit: fixed point reached = False; 6 facts
  Nat(S(S(Zero))) proved: True;  Nat(Banana) proved: False
```

The rule $\mathit{Nat}(x) \Rightarrow \mathit{Nat}(S(x))$ produces a new fact every round, forever. If the query is
entailed, such as $\mathit{Nat}(S(S(\mathit{Zero})))$, it appears in a finite round, so forward chaining is still
complete for definite clauses: *every entailed atom is eventually derived*. But if the query is not entailed, such as
$\mathit{Nat}(\mathit{Banana})$, the program never finds out. This is the first appearance of semi-decidability, the
subject of 9.6.

### Backward chaining

Forward chaining derives everything; most of it may be irrelevant to the question. **Backward chaining** works from the
query instead. To prove a goal, find a clause whose head (conclusion) unifies with it; the clause's premises, with the
unifier applied, become new goals; a fact is a clause with no premises, so unifying with a fact closes the goal. It is
goal-driven, like a person asking "what would I need to know to show this?"

```text
function SOLVE(goals, θ):                       # yields every θ that proves all the goals
    if goals is empty: yield θ; return
    first, rest = goals[0], goals[1:]
    for each clause (head :- body) in the program, with its variables renamed apart:
        θ' = UNIFY(first, head, θ)
        if θ' is not failure:
            yield from SOLVE(body + rest, θ')
```

This is **SLD resolution** (Selective Linear Definite-clause resolution): at each step take the first goal, resolve it
against one clause, and put the clause's body in its place. Figure 9.3 shows the **proof tree** it builds for one
query: an AND tree, because every child must be proved for the parent to hold.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 250" role="img" aria-label="A proof tree. The root Path(Gale, Jezero) is proved by the rule Path(x, z) if Link(x, y) and Path(y, z), with children Link(Gale, Elysium), a fact, and Path(Elysium, Jezero), which is proved by the rule Path(x, y) if Link(x, y), with child Link(Elysium, Jezero), a fact.">
<rect x="225" y="15" width="190" height="34" rx="8" fill="#eea66f" fill-opacity="0.35" stroke="currentColor"/>
<text x="320" y="37" font-size="13" text-anchor="middle" fill="currentColor">Path(Gale, Jezero)</text>
<text x="330" y="74" font-size="12" text-anchor="start" fill="currentColor">rule 2, θ = {x/Gale, z/Jezero}</text>
<line x1="290" y1="49" x2="170" y2="110" stroke="currentColor" stroke-width="1.4"/>
<line x1="350" y1="49" x2="460" y2="110" stroke="currentColor" stroke-width="1.4"/>
<rect x="70" y="110" width="200" height="34" rx="8" fill="#7ccf9a" fill-opacity="0.45" stroke="currentColor"/>
<text x="170" y="132" font-size="13" text-anchor="middle" fill="currentColor">Link(Gale, Elysium)</text>
<text x="170" y="164" font-size="12" text-anchor="middle" fill="currentColor">fact, binds y/Elysium</text>
<rect x="360" y="110" width="200" height="34" rx="8" fill="#eea66f" fill-opacity="0.35" stroke="currentColor"/>
<text x="460" y="132" font-size="13" text-anchor="middle" fill="currentColor">Path(Elysium, Jezero)</text>
<text x="470" y="166" font-size="12" text-anchor="start" fill="currentColor">rule 1</text>
<line x1="460" y1="144" x2="460" y2="195" stroke="currentColor" stroke-width="1.4"/>
<rect x="360" y="195" width="200" height="34" rx="8" fill="#7ccf9a" fill-opacity="0.45" stroke="currentColor"/>
<text x="460" y="217" font-size="13" text-anchor="middle" fill="currentColor">Link(Elysium, Jezero)</text>
<text x="20" y="200" font-size="12" fill="currentColor">rule 1: Path(x, y) :- Link(x, y)</text>
<text x="20" y="220" font-size="12" fill="currentColor">rule 2: Path(x, z) :- Link(x, y), Path(y, z)</text>
</svg>
<figcaption>Figure 9.3. Backward chaining builds an AND tree: to prove the root, prove all its children. Leaves are
facts (green). The binding y/Elysium made at the left leaf is used by the right subtree, which is why the goals are
solved left to right with one shared substitution.</figcaption>
</figure>

Backward chaining has two choices to make at every step: *which goal* to work on (Prolog: the leftmost) and *which
clause* to try first (Prolog: the first in the program, then the next on backtracking). With these fixed choices, it is
a depth-first search of the space of proofs, with all the strengths and weaknesses of depth-first search
([Chapter 3](03-Uninformed-Search.md)): memory linear in the depth of the proof, but no guarantee of finding a proof that
exists, because it can go down an infinite branch first.

### Prolog

**Prolog** ("programmation en logique") was created in 1972 in Marseille by Alain Colmerauer and Philippe Roussel, who
were working on natural-language question answering. Robert Kowalski, then in Edinburgh, supplied the theory: a set of
definite clauses can be read *declaratively*, as statements that are true, or *procedurally*, as a program in which
proving a goal means calling procedures (Kowalski, "Predicate logic as a programming language", 1974). His later
slogan, from a 1979 paper, was *algorithm = logic + control*. David H. D. Warren's 1983 design of an abstract machine
for Prolog (the WAM) made compiled Prolog fast, and most Prolog systems are still built on it.

A Prolog program is a list of definite clauses. In Prolog's own syntax, variables are capitalised and constants are
lower case (the opposite of this chapter), `:-` means "if" and a comma means "and":

```text
append([], L, L).
append([H|T], L, [H|R]) :- append(T, L, R).
```

The two clauses say: appending a list $L$ to the empty list gives $L$; and appending $L$ to a list with head $H$ and
tail $T$ gives a list with head $H$ whose tail is $T$ appended to $L$. Nothing in them says which arguments are inputs.
Our tiny Prolog (lists written as `Cons(head, tail)` and `Nil`) runs the same clauses both ways:

```
3. Backward chaining (a tiny Prolog)
  ?- Append(x, y, [1, 2, 3]).
     x = []         y = [1, 2, 3]
     x = [1]        y = [2, 3]
     x = [1, 2]     y = [3]
     x = [1, 2, 3]  y = []
  ?- Append([1, 2], [3], z).   z = [1, 2, 3]
```

Asked for $z$, it concatenates. Asked for $x$ and $y$, it enumerates all four ways to split the list, one per
backtrack. This running of a relation "backwards" is what makes logic programming feel different from ordinary
programming.

The price is that the declarative reading and the procedural one can disagree. Take a graph of links between Mars
regions (Gale to Elysium, Elysium to Jezero, Jezero to Isidis, and Isidis back to Elysium, a cycle) and two logically
equivalent definitions of a path:

- right-recursive: `Path(x, z) :- Link(x, y), Path(y, z)`;
- left-recursive: `Path(x, z) :- Path(x, y), Link(y, z)`.

Both versions also have the base case `Path(x, y) :- Link(x, y)`. The program, with a depth limit of 40 so that it can
report trouble instead of crashing:

```
  right-recursive: first answers ['Elysium', 'Jezero', 'Isidis', 'Elysium', 'Jezero', 'Isidis'] (46 clause tries)
  left-recursive: first answers ['Elysium', 'Jezero', 'Isidis', 'Elysium', 'Jezero', 'Isidis'] (86 clause tries)
  left-recursive, Path(Jezero, Gale): no answer, depth limit 40 reached (942 clause tries)
  right-recursive, Path(Jezero, Gale): no answer, depth limit 40 reached (182 clause tries)
  forward chaining on the same links reaches a fixed point:
  3 rounds, fixed point True; from Gale: Path(Gale, Elysium), Path(Gale, Isidis), Path(Gale, Jezero)
  Path(Jezero, Gale) in the fixed point: False
```

Three lessons in eight lines:

1. **Repeated answers.** Because of the cycle, there are infinitely many proofs of $\mathit{Path}(\mathit{Gale},
   \mathit{Jezero})$ (go round the loop any number of times), and backward chaining returns an answer for each proof,
   not each fact.
2. **No "no".** $\mathit{Path}(\mathit{Jezero}, \mathit{Gale})$ is false (no link enters Gale), but both versions search
   forever around the cycle without proving or refuting it. In real Prolog this is an infinite loop or a stack
   overflow. The left-recursive version is worse: its first subgoal is $\mathit{Path}(x, y)$ again, so it recurses
   before consuming a single link.
3. **Forward chaining is fine.** The same rules, run bottom-up, stop after 3 rounds, because Datalog has a finite fixed
   point, and the absence of $\mathit{Path}(\mathit{Jezero}, \mathit{Gale})$ from it is a definite "no".

Modern Prolog systems fix this with **tabling** (memoization of subgoals, pioneered in the XSB system in the 1990s):
a subgoal that is already being solved is not re-entered but waits for answers from the first call, which brings
backward chaining the termination of forward chaining on Datalog. It is the same idea as dynamic programming
([Algorithms, Chapter 13](../algorithms/13-Dynamic-Programming.md)). Deductive databases go the other way and run
queries bottom-up, after a "magic sets" rewriting that makes forward chaining derive only facts relevant to the query.

### Negation as failure and the closed world

Prolog has a "not", written `\+`, but it is not logical negation. `\+ G` succeeds when the attempt to prove `G`
*fails*. This is **negation as failure**. Under the **closed-world assumption** (every atom not provable is false), it
is the right reading: a train timetable does not list the trains that do not exist. In logic proper, failing to prove
$G$ does not show $\lnot G$, and adding facts can turn a "yes" from `\+ G` into a "no". That makes Prolog's reasoning
**non-monotonic**, the subject of [11.4](11-Knowledge-Representation.md#114-default-reasoning-and-non-monotonic-logic).

### The chaining program

```python
--8<-- "books/ai/ch09_chaining.py"
```

The full output is the three blocks shown above, in order.

## 9.5 Resolution theorem proving; completeness stated

*Level: intermediate; the completeness sketch is advanced.*

Definite clauses cannot say "Ben or Cleo did it", or "every rover has some camera". For the whole of first-order logic
we need one more tool, and it is the one from [Chapter 8](08-Propositional-Logic-and-SAT.md): **resolution**, lifted to
first-order clauses with unification. John Alan Robinson introduced it in 1965 ("A machine-oriented logic based on the
resolution principle"), together with unification, and the paper changed automated reasoning: instead of generating
ground instances blindly, a prover makes exactly the instances that let two clauses cancel.

To prove $\mathit{KB} \models \alpha$, resolution works by **refutation**: convert $\mathit{KB} \land \lnot\alpha$ to a
set of clauses, and derive the **empty clause** (a contradiction). If it is derived, $\mathit{KB} \land \lnot\alpha$ is
unsatisfiable, which is exactly entailment.

### Clausal form, with Skolem functions

A **clause** is a disjunction of literals (atoms or negated atoms), with all its variables understood as universally
quantified. Any first-order sentence can be turned into a set of clauses that is satisfiable exactly when the sentence
is. The steps, which the program prints for two sentences:

1. **Remove $\Rightarrow$ and $\Leftrightarrow$:** $\alpha \Rightarrow \beta$ becomes $\lnot\alpha \lor \beta$, and
   $\alpha \Leftrightarrow \beta$ becomes $(\lnot\alpha \lor \beta) \land (\lnot\beta \lor \alpha)$.
2. **Push $\lnot$ inward** with De Morgan's laws, for connectives and for quantifiers ($\lnot\forall x\, p$ becomes
   $\exists x\, \lnot p$), and cancel double negations, until negation sits only on atoms.
3. **Rename variables apart**, so that no two quantifiers use the same variable.
4. **Skolemize:** remove each $\exists y$ by replacing $y$ with a new function of the universally quantified variables
   whose scope it is in. If there are none, the function has no arguments: a new constant.
5. **Drop the universal quantifiers;** every remaining variable is universal by convention.
6. **Distribute $\lor$ over $\land$**, giving a conjunction of disjunctions; each disjunction is a clause.

```
1. Clausal form, step by step
  start                    ∀x (Rover(x) ⇒ ∃y (Camera(y) ∧ Has(x, y)))
  remove ⇒ and ⇔           ∀x (~Rover(x) ∨ ∃y (Camera(y) ∧ Has(x, y)))
  push ~ inward            ∀x (~Rover(x) ∨ ∃y (Camera(y) ∧ Has(x, y)))
  rename variables apart   ∀x1 (~Rover(x1) ∨ ∃y2 (Camera(y2) ∧ Has(x1, y2)))
  Skolemize                ∀x1 (~Rover(x1) ∨ (Camera(F1(x1)) ∧ Has(x1, F1(x1))))
  drop ∀                   (~Rover(x1) ∨ (Camera(F1(x1)) ∧ Has(x1, F1(x1))))
  distribute ∨ over ∧      {~Rover(x1), Camera(F1(x1))}   {~Rover(x1), Has(x1, F1(x1))}

  start                    ~∀x (∃y Link(x, y) ⇒ ∀z Visits(z, x))
  remove ⇒ and ⇔           ~∀x (~∃y Link(x, y) ∨ ∀z Visits(z, x))
  push ~ inward            ∃x (∃y Link(x, y) ∧ ∃z ~Visits(z, x))
  rename variables apart   ∃x3 (∃y4 Link(x3, y4) ∧ ∃z5 ~Visits(z5, x3))
  Skolemize                (Link(C1, C2) ∧ ~Visits(C3, C1))
  drop ∀                   (Link(C1, C2) ∧ ~Visits(C3, C1))
  distribute ∨ over ∧      {Link(C1, C2)}   {~Visits(C3, C1)}
```

Skolemization (Thoralf Skolem, 1920s) is the only step that needs thought. In "every rover has a camera", the camera
depends on the rover, so it becomes $F_1(x)$, "the camera of $x$", a function we have never been told about. In the
second sentence, the existentials are not inside any universal (after the negation was pushed in), so they become plain
new constants $C_1, C_2, C_3$: "there is a place $C_1$ and a place $C_2$ linked from it, and someone $C_3$ who has not
visited $C_1$."

**Skolemization preserves satisfiability, not equivalence.** $\exists x\, P(x)$ does not entail $P(C_1)$ for a
particular constant: the knowledge base said nothing about $C_1$. But one is satisfiable exactly when the other is: if a
model makes $\exists x\, P(x)$ true, let $C_1$ name a witness and $P(C_1)$ is true; conversely $P(C_1)$ entails $\exists
x\, P(x)$. The same argument, choosing one witness for each value of the universal variables, works for Skolem functions
(it needs the axiom of choice for infinite domains). Since refutation only asks whether a set is satisfiable, this is
all we need. The Skolem names must be new, never used elsewhere in the knowledge base, or the argument fails.

Step 6 can blow up: $(a_1 \land b_1) \lor \cdots \lor (a_n \land b_n)$ distributes into $2^n$ clauses. Practical
converters introduce new predicate names for subformulas instead (the **Tseitin** transformation, the same trick as in
[Chapter 8](08-Propositional-Logic-and-SAT.md)), which keeps the clause set linear in size.

### The resolution rule

Two clauses, with their variables standardized apart:

$$
\ell_1 \lor \cdots \lor \ell_m \qquad \text{and} \qquad k_1 \lor \cdots \lor k_n.
$$

If some literal $\ell_i$ and the negation of some $k_j$ unify with MGU $\theta$ (that is, one is $P(\ldots)$, the other
is $\lnot P(\ldots)$, and the atoms unify), their **binary resolvent** is

$$
(\ell_1 \lor \cdots \lor \ell_{i-1} \lor \ell_{i+1} \lor \cdots \lor \ell_m \lor k_1 \lor \cdots \lor k_{j-1} \lor k_{j+1} \lor \cdots \lor k_n)\,\theta.
$$

For example, $\lnot \mathit{Rover}(x) \lor \mathit{Camera}(F_1(x))$ and $\mathit{Rover}(\mathit{Percy})$ resolve, with
$\theta = \{x/\mathit{Percy}\}$, to $\mathit{Camera}(F_1(\mathit{Percy}))$.

*Soundness.* Both clauses hold for every value of their variables, so their instances under $\theta$ hold. In the
instances, $\ell_i\theta$ and $k_j\theta$ are complementary: one of them is false in any model. If $\ell_i\theta$ is
false, the rest of the first clause must be true; if $k_j\theta$ is false, the rest of the second is. Either way the
resolvent is true. $\square$

A second rule is needed. **Factoring**: if two literals of the same sign in one clause unify with MGU $\theta$, the
clause with $\theta$ applied (and the duplicate merged) is a **factor**. Why it matters, the program shows. The clauses
$\{P(x), P(y)\}$ and $\{\lnot P(u), \lnot P(v)\}$ are contradictory together (the first says everything is $P$; the
second says nothing is), but every binary resolvent of two-literal clauses here again has two literals, so the empty
clause is unreachable:

```
3. Factoring
  factoring=False: no proof; saturated=True with 3 distinct clauses
  factoring=True: proof found
   1. {~P(v0), ~P(v1)}                             given
   2. {P(v0), P(v1)}                               given
   3. {P(v0)}                                      factor 2
   4. {~P(v0)}                                     resolve 1, 3
   5. {} (empty clause)                            resolve 4, 3
```

Without factoring the prover **saturates**: it runs out of new clauses (three clauses up to renaming) and stops with no
proof, even though the set is unsatisfiable. With factoring, $\{P(x), P(y)\}$ collapses to $\{P(x)\}$ and the proof
takes two more steps. (Robinson's original rule combined the two into one step; the textbook split into binary
resolution plus factoring is equivalent.)

### Two proofs, traced

The prover is a **given-clause loop**, the design of most real provers: keep the clauses in two sets, *processed* and
*unprocessed*; repeatedly move the smallest unprocessed clause (the **given clause**) to the processed set, resolve it
against every processed clause and factor it, and add the new clauses to the unprocessed set, unless they are
duplicates up to renaming or tautologies (contain both $L$ and $\lnot L$). Choosing the smallest first is a version of
the **unit preference** strategy: short clauses are closer to the empty clause.

The first problem: every rover has a camera; anything that has a camera can see; Percy is a rover. Prove that Percy can
see. The negated goal is $\lnot \mathit{CanSee}(\mathit{Percy})$, and the program finds

```
  a rover with a camera can see: prove CanSee(Percy)   (18 clauses generated)
   1. {~Camera(v0), ~Has(v1, v0), CanSee(v1)}      given
   2. {~CanSee(Percy)}                             given
   3. {~Camera(v0), ~Has(Percy, v0)}               resolve 1, 2
   4. {~Rover(v0), Camera(F1(v0))}                 given
   5. {Rover(Percy)}                               given
   6. {Camera(F1(Percy))}                          resolve 4, 5
   7. {~Has(Percy, F1(Percy))}                     resolve 3, 6
   8. {~Rover(v0), Has(v0, F1(v0))}                given
   9. {Has(Percy, F1(Percy))}                      resolve 8, 5
  10. {} (empty clause)                            resolve 7, 9
```

Read it as an argument: "suppose Percy cannot see (2). Then Percy has no camera (3). But Percy is a rover (5), so
$F_1(\mathit{Percy})$ is a camera (6) and Percy has it (9); contradiction (7 with 9)." The prover never learned the
camera's name; the Skolem term $F_1(\mathit{Percy})$ stood in for it.

The second problem: from "every place links to some place" and "two links in a row make a two-step route", prove
"from every place there is a two-step route somewhere", $\forall x\, \exists z\, \mathit{Link2}(x, z)$. Its negation,
after Skolemization, is $\lnot\mathit{Link2}(C_2, z)$: a particular place $C_2$ from which there is no two-step route.

```
  two links make a two-step route: prove all x ex z Link2(x, z)   (10 clauses generated)
   1. {~Link(v0, v1), ~Link(v1, v2), Link2(v0, v2)} given
   2. {Link(v0, F1(v0))}                           given
   3. {~Link(F1(v0), v1), Link2(v0, v1)}           resolve 1, 2
   4. {Link2(v0, F1(F1(v0)))}                      resolve 3, 2
   5. {~Link2(C2, v0)}                             given
   6. {} (empty clause)                            resolve 4, 5
```

Figure 9.4 draws this proof as a tree. Look at clause 4: it says that from any place $v_0$ there is a two-step route to
$F_1(F_1(v_0))$, "the place linked from the place linked from $v_0$". Unification built that nested term by itself.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 300" role="img" aria-label="A resolution refutation tree. Clause 1, not Link(x,y) or not Link(y,z) or Link2(x,z), and clause 2, Link(x, F1(x)), resolve to clause 3. Clause 3 and clause 2 again resolve to clause 4, Link2(x, F1(F1(x))). Clause 4 and the negated goal, not Link2(C2, z), resolve to the empty clause.">
<rect x="10" y="15" width="300" height="32" rx="7" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor"/>
<text x="160" y="36" font-size="13" text-anchor="middle" fill="currentColor">1. ¬Link(x,y) ∨ ¬Link(y,z) ∨ Link2(x,z)</text>
<rect x="390" y="15" width="170" height="32" rx="7" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor"/>
<text x="475" y="36" font-size="13" text-anchor="middle" fill="currentColor">2. Link(x, F1(x))</text>
<line x1="160" y1="47" x2="230" y2="95" stroke="currentColor" stroke-width="1.3"/>
<line x1="475" y1="47" x2="330" y2="95" stroke="currentColor" stroke-width="1.3"/>
<rect x="150" y="95" width="260" height="32" rx="7" fill="#eea66f" fill-opacity="0.35" stroke="currentColor"/>
<text x="280" y="116" font-size="13" text-anchor="middle" fill="currentColor">3. ¬Link(F1(x), z) ∨ Link2(x, z)</text>
<text x="420" y="80" font-size="12" text-anchor="start" fill="currentColor">θ = {y/F1(x)}</text>
<line x1="280" y1="127" x2="300" y2="175" stroke="currentColor" stroke-width="1.3"/>
<line x1="520" y1="47" x2="350" y2="175" stroke="currentColor" stroke-width="1.3" stroke-dasharray="5 3"/>
<text x="450" y="150" font-size="12" text-anchor="start" fill="currentColor">2 again, θ = {z/F1(F1(x))}</text>
<rect x="200" y="175" width="220" height="32" rx="7" fill="#eea66f" fill-opacity="0.35" stroke="currentColor"/>
<text x="310" y="196" font-size="13" text-anchor="middle" fill="currentColor">4. Link2(x, F1(F1(x)))</text>
<rect x="10" y="175" width="160" height="32" rx="7" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor"/>
<text x="90" y="196" font-size="13" text-anchor="middle" fill="currentColor">5. ¬Link2(C2, z)</text>
<line x1="90" y1="207" x2="190" y2="250" stroke="currentColor" stroke-width="1.3"/>
<line x1="310" y1="207" x2="230" y2="250" stroke="currentColor" stroke-width="1.3"/>
<rect x="150" y="250" width="120" height="32" rx="7" fill="#7ccf9a" fill-opacity="0.5" stroke="currentColor"/>
<text x="210" y="271" font-size="13" text-anchor="middle" fill="currentColor">6. empty</text>
<text x="290" y="271" font-size="12" text-anchor="start" fill="currentColor">θ = {x/C2, z/F1(F1(C2))}</text>
</svg>
<figcaption>Figure 9.4. The refutation as a tree: blue clauses come from the knowledge base and the negated goal,
orange ones are resolvents, and the green leaf is the contradiction. Clause 2 is used twice, each time with its
variables renamed apart.</figcaption>
</figure>

### Answer extraction

A refutation shows that *some* $x$ exists; often we want to know *which*. Cordell Green's trick (1969) is to add a
literal $\mathit{Answer}(w)$ to the negated query clause and stop when a clause containing only $\mathit{Answer}$
literals appears. The bindings made along the way fill in $w$:

```
4. Answer extraction: who is a grandchild of Ada?
   1. {~Parent(v0, v1), ~Parent(v1, v2), Grandparent(v0, v2)} given
   2. {Parent(Ada, Ben)}                           given
   3. {~Parent(Ben, v0), Grandparent(Ada, v0)}     resolve 1, 2
   4. {Parent(Ben, Dan)}                           given
   5. {Grandparent(Ada, Dan)}                      resolve 3, 4
   6. {~Grandparent(Ada, v0), Answer(v0)}          given
   7. {Answer(Dan)}                                resolve 5, 6
```

Prolog's answers are the same idea: the substitution that closes the proof is the answer. With disjunctive knowledge,
the answer clause can be $\mathit{Answer}(\mathit{Ben}) \lor \mathit{Answer}(\mathit{Cleo})$: the knowledge base proves
that one of them is the answer, but not which. Logic is honest about that.

### Completeness

**Theorem (refutation completeness, Robinson 1965).** If a set of clauses is unsatisfiable, then resolution with
factoring derives the empty clause from it in finitely many steps.

This is the deepest result of the chapter, and the proof is too long to give in full; here is its skeleton, with the
full proof in Russell and Norvig (section 9.5) or Chang and Lee (1973).

1. **Herbrand's theorem.** Let $S$ be a set of clauses. Its **Herbrand universe** $H_S$ is the set of all ground terms
   built from the constants and function symbols of $S$ (with one invented constant if $S$ has none). The theorem: if
   $S$ is unsatisfiable, then some *finite* set of ground instances of clauses of $S$ (instances with terms from
   $H_S$) is unsatisfiable, as a propositional set. The reason is that if $S$ has any model, it has one whose domain is
   $H_S$ itself; and propositional compactness turns "every finite subset of the ground instances is satisfiable" into
   "the whole infinite set is satisfiable".
2. **Ground completeness.** By the propositional completeness of resolution ([Chapter 8](08-Propositional-Logic-and-SAT.md)),
   that finite ground set has a resolution refutation using ground clauses.
3. **Lifting lemma.** If $C_1'$ and $C_2'$ are ground instances of $C_1$ and $C_2$, and $C'$ is a resolvent of $C_1'$
   and $C_2'$, then there is a resolvent $C$ of $C_1$ and $C_2$ (after factoring, if needed) such that $C'$ is an
   instance of $C$. Unification is exactly what makes this true: the MGU is general enough that every ground step has a
   first-order step above it. (The factoring example above is the case where two ground literals coincide only after
   instantiation, so the first-order step must merge them first.)
4. Lift the ground refutation step by step. The ground empty clause is an instance only of the empty clause, so the
   lifted proof ends in the empty clause too. $\square$

Completeness says a proof *exists*; it does not say the prover finds it quickly, and it does not say what happens when
there is no proof. The given-clause loop with a fair selection order (every clause is eventually chosen) does find
every refutation that exists. On a satisfiable set, though, it may generate new clauses forever. 9.6 shows this is not a
weakness of resolution but of every possible method.

### Strategies and equality

A naive prover drowns in resolvents. Decades of work have produced **restrictions** that keep completeness while
cutting the search:

- **Set of support** (Wos, Robinson and Carson, 1965): every resolution step must involve a clause derived from the
  negated goal. The knowledge base is assumed consistent, so contradictions must come from the goal. Complete.
- **Subsumption:** delete a clause if a more general one is already present ($P(x)$ makes $P(A) \lor Q(B)$ useless).
- **Input and linear resolution:** each step uses an input clause, or the previous resolvent. SLD resolution in Prolog
  is linear input resolution restricted to definite clauses, where it is complete.
- **Ordered resolution:** resolve only on the largest literal of each clause under a fixed ordering of atoms.

Equality needs its own rules: treating $=$ as an ordinary predicate with axioms for reflexivity, symmetry,
transitivity and substitution works but is hopeless in practice. **Demodulation** rewrites terms with known equations;
**paramodulation** (Robinson and Wos, 1969) is a resolution-like rule for equalities; **superposition** (Bachmair and
Ganzinger, early 1990s) combines paramodulation with orderings, and it is the calculus inside the strongest modern
first-order provers, such as Vampire and E. A well-known success: in 1996 William McCune's prover EQP found a proof
that every Robbins algebra is a Boolean algebra, settling a question posed in the 1930s (McCune, "Solution of the
Robbins problem", *Journal of Automated Reasoning*, 1997).

In practice, few people write resolution provers by hand. Logic programs run in Prolog systems (SWI-Prolog, for
example); Datalog runs in deductive databases; full first-order problems go to provers such as Vampire or E, which
compete each year in the CASC competition on problems from the TPTP library; and problems mixing logic with arithmetic,
arrays and bit-vectors go to SMT solvers ("satisfiability modulo theories"), such as Z3, which grow out of the CDCL SAT
solvers of [Chapter 8](08-Propositional-Logic-and-SAT.md).

### The resolution program

```python
--8<-- "books/ai/ch09_resolution.py"
```

```
1. Clausal form, step by step
  start                    ∀x (Rover(x) ⇒ ∃y (Camera(y) ∧ Has(x, y)))
  remove ⇒ and ⇔           ∀x (~Rover(x) ∨ ∃y (Camera(y) ∧ Has(x, y)))
  push ~ inward            ∀x (~Rover(x) ∨ ∃y (Camera(y) ∧ Has(x, y)))
  rename variables apart   ∀x1 (~Rover(x1) ∨ ∃y2 (Camera(y2) ∧ Has(x1, y2)))
  Skolemize                ∀x1 (~Rover(x1) ∨ (Camera(F1(x1)) ∧ Has(x1, F1(x1))))
  drop ∀                   (~Rover(x1) ∨ (Camera(F1(x1)) ∧ Has(x1, F1(x1))))
  distribute ∨ over ∧      {~Rover(x1), Camera(F1(x1))}   {~Rover(x1), Has(x1, F1(x1))}

  start                    ~∀x (∃y Link(x, y) ⇒ ∀z Visits(z, x))
  remove ⇒ and ⇔           ~∀x (~∃y Link(x, y) ∨ ∀z Visits(z, x))
  push ~ inward            ∃x (∃y Link(x, y) ∧ ∃z ~Visits(z, x))
  rename variables apart   ∃x3 (∃y4 Link(x3, y4) ∧ ∃z5 ~Visits(z5, x3))
  Skolemize                (Link(C1, C2) ∧ ~Visits(C3, C1))
  drop ∀                   (Link(C1, C2) ∧ ~Visits(C3, C1))
  distribute ∨ over ∧      {Link(C1, C2)}   {~Visits(C3, C1)}

2. Proofs by refutation
  a rover with a camera can see: prove CanSee(Percy)   (18 clauses generated)
   1. {~Camera(v0), ~Has(v1, v0), CanSee(v1)}      given
   2. {~CanSee(Percy)}                             given
   3. {~Camera(v0), ~Has(Percy, v0)}               resolve 1, 2
   4. {~Rover(v0), Camera(F1(v0))}                 given
   5. {Rover(Percy)}                               given
   6. {Camera(F1(Percy))}                          resolve 4, 5
   7. {~Has(Percy, F1(Percy))}                     resolve 3, 6
   8. {~Rover(v0), Has(v0, F1(v0))}                given
   9. {Has(Percy, F1(Percy))}                      resolve 8, 5
  10. {} (empty clause)                            resolve 7, 9

  two links make a two-step route: prove all x ex z Link2(x, z)   (10 clauses generated)
   1. {~Link(v0, v1), ~Link(v1, v2), Link2(v0, v2)} given
   2. {Link(v0, F1(v0))}                           given
   3. {~Link(F1(v0), v1), Link2(v0, v1)}           resolve 1, 2
   4. {Link2(v0, F1(F1(v0)))}                      resolve 3, 2
   5. {~Link2(C2, v0)}                             given
   6. {} (empty clause)                            resolve 4, 5

3. Factoring
  factoring=False: no proof; saturated=True with 3 distinct clauses
  factoring=True: proof found
   1. {~P(v0), ~P(v1)}                             given
   2. {P(v0), P(v1)}                               given
   3. {P(v0)}                                      factor 2
   4. {~P(v0)}                                     resolve 1, 3
   5. {} (empty clause)                            resolve 4, 3

4. Answer extraction: who is a grandchild of Ada?
   1. {~Parent(v0, v1), ~Parent(v1, v2), Grandparent(v0, v2)} given
   2. {Parent(Ada, Ben)}                           given
   3. {~Parent(Ben, v0), Grandparent(Ada, v0)}     resolve 1, 2
   4. {Parent(Ben, Dan)}                           given
   5. {Grandparent(Ada, Dan)}                      resolve 3, 4
   6. {~Grandparent(Ada, v0), Answer(v0)}          given
   7. {Answer(Dan)}                                resolve 5, 6
```

## 9.6 Limits: semi-decidability, completeness and incompleteness

*Level: advanced.*

Forward chaining on $\mathit{Nat}$ never stopped, and backward chaining on $\mathit{Path}(\mathit{Jezero},
\mathit{Gale})$ never stopped. Is that a flaw of our programs, to be fixed by a cleverer one? This section answers: no.
It is a theorem about first-order logic itself.

### Decidable, semi-decidable, undecidable

A yes/no problem is **decidable** if some algorithm always halts with the right answer. It is **semi-decidable**
(also *recursively enumerable*) if some algorithm halts with "yes" on every yes-instance, and on no-instances either
says "no" or runs forever. Propositional entailment is decidable: a truth table has finitely many rows
([Chapter 8](08-Propositional-Logic-and-SAT.md)). Datalog entailment is decidable: the fixed point is finite (9.4).

**Theorem (Church 1936; Turing 1936).** Validity of first-order sentences is undecidable: no algorithm takes an
arbitrary sentence $\varphi$ and always halts with the correct answer to "is $\varphi$ valid?". Equivalently, no
algorithm decides $\mathit{KB} \models \alpha$ for arbitrary finite $\mathit{KB}$ and $\alpha$.

This answered, negatively, the *Entscheidungsproblem* ("decision problem") that David Hilbert and Wilhelm Ackermann had
posed in 1928. Alonzo Church proved it using his lambda calculus ("A note on the Entscheidungsproblem", 1936), and Alan
Turing independently, in the paper that introduced Turing machines ("On computable numbers, with an application to the
Entscheidungsproblem", 1936).

*Proof idea (Turing's route).* The halting problem is undecidable: no algorithm decides whether a given Turing machine
halts on an empty tape ([Algorithms, Chapter 1](../algorithms/01-What-Is-an-Algorithm.md) and the Logic book's
[Undecidability](https://math.akadian.ca/books/logic/14-Undecidability.html)). For any machine $M$, write a finite set
of first-order sentences $\mathit{KB}_M$ that describes its computation: a constant $0$ and a successor function for
time steps and tape positions; a predicate $\mathit{State}_q(t)$ for "at time $t$ the machine is in state $q$", a
predicate $\mathit{Head}(t, p)$, predicates $\mathit{Sym}_a(t, p)$ for "at time $t$ cell $p$ holds symbol $a$"; one
axiom for the start configuration and one axiom per transition rule of $M$, saying how the configuration at time
$S(t)$ follows from the one at time $t$. These are definite clauses. By induction on $t$, $\mathit{KB}_M$ entails the
atom describing step $t$ of the real computation, and (by looking at the model built from the real computation)
nothing else about states. So $\mathit{KB}_M \models \exists t\, \mathit{State}_{\mathit{halt}}(t)$ exactly when $M$
halts. A decision procedure for entailment would therefore decide the halting problem, which is impossible. $\square$

Notice that the encoding uses only definite clauses with one function symbol. So even backward and forward chaining
over definite clauses with functions, that is, Prolog, cannot be made always to halt. Prolog is a full programming
language, and the halting problem comes with that.

**Theorem (semi-decidability).** Entailment in first-order logic is semi-decidable: there is an algorithm that halts
with "yes" exactly when $\mathit{KB} \models \alpha$.

*Proof.* Run resolution on the clauses of $\mathit{KB} \land \lnot\alpha$ with a fair strategy (breadth-first over
the possible resolution steps, for instance). If $\mathit{KB} \models \alpha$, the set is unsatisfiable, so by
refutation completeness a refutation exists, and it has finite length, so the fair search finds it and halts. If not,
there is no refutation and the search may run forever. $\square$

The two theorems together say: **the non-entailed sentences are not semi-decidable.** If they were, we could run the
"yes" search and the "no" search side by side, one step each in turn; one of them must halt, and we would have a
decision procedure, contradicting Church and Turing. So the asymmetry is permanent. A prover that has not found a proof
after an hour has told you nothing; maybe the proof is on the next step, maybe there is none.

### Gödel's completeness theorem

Resolution is one complete proof procedure. The first was Gödel's.

**Theorem (Gödel's completeness theorem, 1929 thesis, published 1930).** There is a sound proof system for first-order
logic in which every valid sentence is provable; more generally, $\mathit{KB} \models \alpha$ implies
$\mathit{KB} \vdash \alpha$.

Here $\vdash$ means "derivable by the rules of the system", a purely mechanical notion, and $\models$ means "true in
every model", a notion about all possible worlds, including infinite ones. Completeness says that the mechanical notion
catches up with the semantic one. Its consequences for AI are concrete: since proofs are finite objects that can be
listed one by one, valid sentences can be enumerated, which is the semi-decidability above; and it gives the
**compactness theorem**: if every finite subset of a set of sentences has a model, the whole set has one (a proof of a
contradiction would use only finitely many sentences).

### Gödel's incompleteness theorem

**Theorem (Gödel's first incompleteness theorem, 1931).** Any consistent theory, with axioms that an algorithm can
list, that contains enough arithmetic (addition and multiplication of natural numbers) has a sentence $G$ in its
language such that neither $G$ nor $\lnot G$ is provable from the axioms. In particular, some sentences true of the
natural numbers are not provable.

How can both theorems be true? They talk about different things. **Completeness** concerns sentences true in *every*
model of the axioms. **Incompleteness** concerns sentences true in *one intended* model, the natural numbers
$\mathbb{N}$ with ordinary addition and multiplication. Gödel's sentence $G$ is true in $\mathbb{N}$ but false in some
other model of the same axioms (a **nonstandard model** of arithmetic, which contains elements beyond all of $0, S(0),
S(S(0)), \ldots$). Since $G$ is not true in every model, completeness does not promise a proof of it, and there is no
contradiction. What incompleteness shows is that first-order axioms cannot pin down $\mathbb{N}$ uniquely. Compactness
shows the same thing directly: add a new constant $c$ and the sentences $c \neq 0$, $c \neq S(0)$, $c \neq S(S(0))$,
...; every finite subset has a model (interpret $c$ as a large enough number), so the whole set does, and in that model
$c$ is a "number" larger than every standard one. The Logic book proves both theorems
([Completeness and compactness](https://math.akadian.ca/books/logic/11-Completeness-and-Compactness.html),
[Gödel's incompleteness theorems](https://math.akadian.ca/books/logic/18-Godels-Incompleteness-Theorems.html)).

### What first-order logic cannot say

Compactness also limits expressiveness. The $\mathit{Ancestor}$ definition of 9.2 is an example.

**Claim.** No first-order formula $\varphi(x, y)$ can say "$y$ is reachable from $x$ by a finite chain of
$\mathit{Parent}$ links" in every model.

*Proof.* Suppose $\varphi$ did. Add two new constants $a$ and $b$, the sentence $\varphi(a, b)$, and for each $n \geq 1$
the sentence $\psi_n$ = "there is no chain of $n$ Parent links from $a$ to $b$" (a first-order sentence with $n - 1$
existential variables for the intermediate people, all negated). Any finite subset mentions only $\psi_n$ for
$n < N$ for some $N$; it is satisfied by a chain of exactly $N$ links from $a$ to $b$. By compactness the whole set has
a model. In it, $\varphi(a, b)$ holds, so $b$ is reachable from $a$ by some finite chain of some length $n$, but
$\psi_n$ also holds, a contradiction. $\square$

So the biconditional for $\mathit{Ancestor}$ in 9.2 has models in which $\mathit{Ancestor}$ is bigger than the real
relation. Logic programs and Datalog sidestep this: they read rules as defining the **least** fixed point, the smallest
relation closed under the rules, which is exactly what forward chaining computes. This "least model" reading is a step
outside pure first-order semantics, and it is one reason databases and Prolog are more convenient than raw logic for
recursive definitions. Similarly, no first-order sentence is true exactly in the finite models (Exercise 11).

**Second-order logic**, with variables over relations, *can* say all these things (and it pins down $\mathbb{N}$ up to
isomorphism). The price: it has no complete, sound and effective proof system at all. First-order logic sits at a sweet
spot, expressive enough for most of mathematics (through set theory) and with a complete proof procedure; Lindström's
theorem (Per Lindström, 1969) makes this precise, showing that no logic extending first-order logic keeps both
compactness and the downward Löwenheim-Skolem property.

### Decidable fragments

Because full FOL is undecidable, much of applied logic works in **fragments** that are decidable and still useful.
Figure 9.5 places the ones in this book.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 300" role="img" aria-label="Nested regions. The outer region, true arithmetic, is not even semi-decidable. Inside it, full first-order logic and Horn clauses with functions (Prolog) are semi-decidable but undecidable. Inside that, a decidable region contains propositional logic, Datalog, monadic first-order logic, the two-variable fragment and description logics.">
<rect x="10" y="10" width="620" height="280" rx="16" fill="#eea66f" fill-opacity="0.15" stroke="currentColor"/>
<text x="24" y="34" font-size="13" fill="currentColor" font-weight="bold">not even semi-decidable</text>
<text x="24" y="52" font-size="12" fill="currentColor">truths of arithmetic (Gödel 1931); second-order validity</text>
<rect x="40" y="66" width="560" height="208" rx="14" fill="#9cc9ea" fill-opacity="0.25" stroke="currentColor"/>
<text x="56" y="90" font-size="13" fill="currentColor" font-weight="bold">semi-decidable, undecidable</text>
<text x="56" y="108" font-size="12" fill="currentColor">full first-order logic (resolution finds every proof);</text>
<text x="56" y="124" font-size="12" fill="currentColor">definite clauses with function symbols (Prolog)</text>
<rect x="70" y="138" width="500" height="120" rx="12" fill="#7ccf9a" fill-opacity="0.3" stroke="currentColor"/>
<text x="86" y="162" font-size="13" fill="currentColor" font-weight="bold">decidable</text>
<text x="86" y="182" font-size="12" fill="currentColor">propositional logic (NP-complete satisfiability, Chapter 8)</text>
<text x="86" y="200" font-size="12" fill="currentColor">Datalog (polynomial for a fixed program)</text>
<text x="86" y="218" font-size="12" fill="currentColor">monadic first-order logic; the two-variable fragment</text>
<text x="86" y="236" font-size="12" fill="currentColor">∃*∀* sentences without functions; description logics (Chapter 11)</text>
</svg>
<figcaption>Figure 9.5. Where the logics of this part of the book sit. Moving inward buys termination at the price of
expressiveness; most real knowledge-based systems live in the green region, and reach outward only with care.</figcaption>
</figure>

- **Monadic FOL** (only one-place predicates, no functions) is decidable (Leopold Löwenheim, 1915).
- **The two-variable fragment** (any formula using only two variable names, reused freely) is decidable (Dana Scott,
  1962, without equality; Michael Mortimer, 1975, with it).
- **The Bernays-Schönfinkel class**: sentences of the form $\exists x_1 \ldots \exists x_m\, \forall y_1 \ldots \forall
  y_n\, \varphi$ with no function symbols. After Skolemization these have only constants, so the Herbrand universe is
  finite, and the problem reduces to a large propositional one. Planning problems ([Chapter 10](10-Planning.md)) and
  many verification problems fit here.
- **Description logics**, the logics of ontologies, are carefully chosen decidable fragments; they are the subject of
  [11.2](11-Knowledge-Representation.md#112-semantic-networks-and-frames-description-logics).

### A short history thread

Gottlob Frege's *Begriffsschrift* (1879) introduced quantifiers and the first complete formal system of predicate
logic. Whitehead and Russell's *Principia Mathematica* (1910-1913) tried to derive mathematics from logic. Hilbert's
programme in the 1920s asked for a complete, consistent, decidable foundation; Gödel (1930, 1931), Church and Turing
(1936) showed which parts of that wish could be granted (completeness) and which could not (decidability, completeness
for arithmetic). The machine age began with the Logic Theorist of Newell, Shaw and Simon (1956), which proved theorems
of *Principia* by heuristic search ([Chapter 1](01-What-Is-AI.md)); Gilmore (1960) and Davis and Putnam (1960) built
Herbrand-style provers; Robinson (1965) gave unification and resolution; Green (1969) used resolution to answer
questions and to plan, which leads into [Chapter 10](10-Planning.md); Colmerauer, Roussel and Kowalski (1972-1974) turned
definite-clause resolution into Prolog. Today the descendants of these ideas are interactive proof assistants (Lean,
Coq, Isabelle), automated provers inside them, SMT solvers that check software and hardware, and Datalog engines that
analyse programs.

## Check yourself

??? question "1. Write in first-order logic: (a) Every crater that contains a lake bed is a target. (b) Some rover has visited every crater. (c) No rover has visited Olympus Mons."

    (a) $\forall c\, (\mathit{Crater}(c) \land \mathit{ContainsLakeBed}(c) \Rightarrow \mathit{Target}(c))$. The
    universal goes with $\Rightarrow$.

    (b) $\exists r\, (\mathit{Rover}(r) \land \forall c\, (\mathit{Crater}(c) \Rightarrow \mathit{Visited}(r, c)))$. The
    existential goes with $\land$, the inner universal with $\Rightarrow$, and the order $\exists r\, \forall c$ says
    one rover visited them all (with $\forall c\, \exists r$ each crater could have a different rover).

    (c) $\lnot \exists r\, (\mathit{Rover}(r) \land \mathit{Visited}(r, \mathit{OlympusMons}))$, or equivalently
    $\forall r\, (\mathit{Rover}(r) \Rightarrow \lnot\mathit{Visited}(r, \mathit{OlympusMons}))$.

??? question "2. Push the negation all the way in: ¬∀x ∃y (Link(x, y) ∧ ¬Visited(y)). Then say in words what the result means."

    $\lnot\forall x\, \exists y\, (\ldots) \equiv \exists x\, \lnot\exists y\, (\ldots) \equiv \exists x\, \forall y\,
    \lnot(\mathit{Link}(x, y) \land \lnot\mathit{Visited}(y)) \equiv \exists x\, \forall y\, (\lnot\mathit{Link}(x, y)
    \lor \mathit{Visited}(y))$. In words: there is a place $x$ such that every place linked from it has been visited
    (equivalently, $\forall y\, (\mathit{Link}(x, y) \Rightarrow \mathit{Visited}(y))$).

??? question "3. Find the most general unifier, or show that none exists: (a) P(x, g(x), z) and P(A, y, f(y)); (b) Q(f(x), x) and Q(y, A); (c) R(x, f(x)) and R(f(y), y); (d) Older(Father(y), y) and Older(Father(x), John); (e) Knows(Father(y), y) and Knows(x, x)."

    (a) $x = A$; then $g(A) = y$ binds $y$; then $z = f(y) = f(g(A))$. MGU $\{x/A, y/g(A), z/f(g(A))\}$.

    (b) $f(x) = y$ binds $y/f(x)$; $x = A$. In solved form $\{x/A, y/f(A)\}$.

    (c) $x = f(y)$; then $f(x) = y$ becomes $f(f(y)) = y$, and $y$ occurs in $f(f(y))$: the occurs check fails, no
    unifier.

    (d) Decompose: $\mathit{Father}(y) = \mathit{Father}(x)$ gives $y = x$; then $y = \mathit{John}$. MGU
    $\{y/\mathit{John}, x/\mathit{John}\}$.

    (e) $\mathit{Father}(y) = x$ binds $x$; then $y = x = \mathit{Father}(y)$: occurs check, no unifier. All five agree with `unify` in the program.

??? question "4. A query Knows(John, x) and a fact Knows(x, Elizabeth) do not unify. Explain why that is the wrong answer, and what the fix is."

    The fact means $\forall x\, \mathit{Knows}(x, \mathit{Elizabeth})$ and the query asks for some $x$ with
    $\mathit{Knows}(\mathit{John}, x)$. The two $x$'s are bound by different quantifiers, so they are different
    variables; the answer should be $x = \mathit{Elizabeth}$. The fix is **standardizing apart**: rename the variables
    of one side before unifying, e.g. the fact becomes $\mathit{Knows}(z, \mathit{Elizabeth})$, and the MGU is
    $\{z/\mathit{John}, x/\mathit{Elizabeth}\}$.

??? question "5. Convert to clausal form: ∀x (Rover(x) ⇒ ∃y (Site(y) ∧ ∀z (Sample(z) ∧ From(z, y) ⇒ Analyzed(x, z))))."

    Remove $\Rightarrow$: $\forall x\, (\lnot\mathit{Rover}(x) \lor \exists y\, (\mathit{Site}(y) \land \forall z\,
    (\lnot\mathit{Sample}(z) \lor \lnot\mathit{From}(z, y) \lor \mathit{Analyzed}(x, z))))$. The negations are already
    on atoms. Skolemize: $y$ is inside $\forall x$ only, so $y$ becomes $F(x)$, "the site chosen for rover $x$". Drop
    the universals and distribute:

    - $\lnot\mathit{Rover}(x) \lor \mathit{Site}(F(x))$
    - $\lnot\mathit{Rover}(x) \lor \lnot\mathit{Sample}(z) \lor \lnot\mathit{From}(z, F(x)) \lor \mathit{Analyzed}(x, z)$

    This is what `to_clauses` prints (with the Skolem function named `F1`).

??? question "6. Skolemize ∃y ∀x Loves(x, y) and ∀x ∃y Loves(x, y). Why do the answers differ, and why does it matter that the Skolem symbols are new?"

    $\exists y\, \forall x\, \mathit{Loves}(x, y)$ becomes $\mathit{Loves}(x, C)$: one beloved $C$ for everybody.
    $\forall x\, \exists y\, \mathit{Loves}(x, y)$ becomes $\mathit{Loves}(x, F(x))$: the beloved depends on the lover.
    The Skolem term's arguments record exactly which universals the existential depends on, which is how clausal form
    keeps the difference between the two sentences. If the new symbol were an existing one, say $\mathit{Ada}$, the
    clause would claim that everyone loves Ada, which does not follow and can make a satisfiable knowledge base
    unsatisfiable.

??? question "7. Write the code: run forward chaining with only the two ancestor rules on a chain of n people P0 → P1 → ... → P(n-1), for n = 2, 3, 5, 8. How many rounds and how many Ancestor facts? Explain the pattern."

    ```python
    from ch09_chaining import forward_chain, rule

    for n in [2, 3, 5, 8]:
        people = [f"P{i}" for i in range(n)]
        facts = {("Parent", people[i], people[i + 1]) for i in range(n - 1)}
        kb, rounds, fixed = forward_chain(facts, [rule("Parent(x, y) => Ancestor(x, y)"),
                                                  rule("Parent(x, y) & Ancestor(y, z) => Ancestor(x, z)")],
                                          quiet=True)
        print(n, rounds, sum(1 for f in kb if f[0] == "Ancestor"))
    ```

    Output (run from the code folder):

    ```
    2 1 1
    3 2 3
    5 4 10
    8 7 28
    ```

    Round $r$ adds exactly the pairs $r$ generations apart: a pair at distance $r$ needs a parent link plus an ancestor
    pair at distance $r - 1$, which first exists after round $r - 1$. Distances go from 1 to $n - 1$, so there are
    $n - 1$ productive rounds, and the number of pairs is $\binom{n}{2} = n(n-1)/2$.

??? question "8. Write the code: add Member and Reverse to the tiny Prolog and ask Member(w, [A, B, C]) and Reverse([A, B, C], r)."

    ```python
    from ch09_chaining import clause, solve, plist, show_list
    from ch09_unify import substitute, show

    prog = [clause("Member(x, Cons(x, t))"),
            clause("Member(x, Cons(h, t)) :- Member(x, t)"),
            clause("Append(Nil, l, l)"),
            clause("Append(Cons(h, t), l, Cons(h, r)) :- Append(t, l, r)"),
            clause("Reverse(Nil, Nil)"),
            clause("Reverse(Cons(h, t), r) :- Reverse(t, rt) & Append(rt, Cons(h, Nil), r)")]
    q = ("Member", "?w", plist(["A", "B", "C"]))
    print([show(substitute("?w", s)) for s in solve([q], prog, {}, 0, 50)])
    q = ("Reverse", plist(["A", "B", "C"]), "?r")
    print(show_list(substitute("?r", next(solve([q], prog, {}, 0, 50)))))
    ```

    It prints `['A', 'B', 'C']` and `[C, B, A]`. The first clause of Member says $x$ is a member of a list that starts
    with $x$; the second says it is a member if it is a member of the tail. Asked with $w$ unbound, backtracking
    enumerates the members in order. This Reverse is "naive reverse": it calls Append on lists of length
    $0, 1, \ldots, n-1$, so it takes $\Theta(n^2)$ steps; a version with an accumulator argument takes $\Theta(n)$.
    Run the other way, `Reverse(r, [A, B, C])`, it finds `r = [C, B, A]` first, but asking for a second answer
    sends it searching longer and longer lists forever (the program's depth limit reports it). The logic is symmetric;
    the depth-first control is not.

??? question "9. Prove by resolution: every dusty rover is not charged; every rover is charged or asleep; Spirit is a dusty rover. Therefore Spirit is asleep. Why can't backward chaining on definite clauses do this?"

    Clauses: (1) $\lnot\mathit{Rover}(x) \lor \lnot\mathit{Dusty}(x) \lor \lnot\mathit{Charged}(x)$; (2)
    $\lnot\mathit{Rover}(x) \lor \mathit{Charged}(x) \lor \mathit{Asleep}(x)$; (3) $\mathit{Rover}(\mathit{Spirit})$;
    (4) $\mathit{Dusty}(\mathit{Spirit})$; (5) negated goal $\lnot\mathit{Asleep}(\mathit{Spirit})$.

    Resolve 2 with 3: $\mathit{Charged}(\mathit{Spirit}) \lor \mathit{Asleep}(\mathit{Spirit})$. With 5:
    $\mathit{Charged}(\mathit{Spirit})$. Resolve 1 with 3: $\lnot\mathit{Dusty}(\mathit{Spirit}) \lor
    \lnot\mathit{Charged}(\mathit{Spirit})$; with 4: $\lnot\mathit{Charged}(\mathit{Spirit})$. Resolve with
    $\mathit{Charged}(\mathit{Spirit})$: the empty clause. The program's `prove` finds the same 10-line proof.

    Clause 2 has two positive literals, so it is not a definite clause, and clause 1 has none (it is a constraint).
    Backward chaining needs every clause to have exactly one head; here the proof is a case analysis ("charged or
    asleep; not charged; so asleep"), which needs resolution.

??? question "10. Write the code: use the prover to show that the 'drinker sentence' ∃x (D(x) ⇒ ∀y D(y)) is valid. Explain the proof in words."

    ```python
    from ch09_resolution import F, prove, to_clauses

    clauses = to_clauses(("~", F("ex x (D(x) => all y D(y))")))
    print(clauses)
    proof, kept, saturated = prove(clauses)
    print("\n".join(proof))
    ```

    The negation becomes $\forall x\, (D(x) \land \exists y\, \lnot D(y))$, so the clauses are $D(x)$ and
    $\lnot D(F_1(x))$. They resolve at once, with $\{x/F_1(x')\}$, to the empty clause; the prover prints a three-line
    proof. In words: either everyone is $D$, and then any $x$ works; or someone is not $D$, and then choosing that
    person as $x$ makes $D(x)$ false and the implication true. The sentence sounds paradoxical ("there is someone such
    that if they drink, everyone drinks") only because it reads like a causal claim.

??? question "11. (Advanced) Use compactness to show that no first-order sentence φ is true in exactly the finite models."

    For each $n$, the sentence $\lambda_n = \exists x_1 \ldots \exists x_n \bigwedge_{i<j} x_i \neq x_j$ says "there
    are at least $n$ objects". Suppose $\varphi$ held exactly in the finite models. Consider $\{\varphi, \lambda_1,
    \lambda_2, \ldots\}$. A finite subset contains $\lambda_n$ only for $n \le N$; a model with $N$ objects satisfies it
    (it is finite, so it satisfies $\varphi$). By compactness the whole set has a model; it satisfies every
    $\lambda_n$, so it is infinite, and it satisfies $\varphi$, so it is finite. Contradiction.

??? question "12. (Advanced) Explain why entailment and non-entailment cannot both be semi-decidable, and what a theorem prover that has run for a week without a proof tells you."

    If an algorithm $A$ halted exactly on entailed queries and an algorithm $B$ exactly on non-entailed ones, we could
    run them alternately one step at a time; exactly one halts on each query, and we would have a decision procedure.
    Church and Turing proved no decision procedure exists. Entailment is semi-decidable (complete resolution with a fair
    strategy), so non-entailment is not. A week without a proof is therefore no evidence of non-entailment in general:
    the proof might be very long, or not exist. In practice, provers report "unknown" on a timeout, and some also try to
    find a finite counter-model (a model of $\mathit{KB} \land \lnot\alpha$), which, when it exists and is found, is a
    real "no".

## What you learned

- First-order logic talks about objects, relations and functions, with $\forall$ and $\exists$; one sentence can
  state a law that propositional logic needs thousands of sentences for, or cannot state at all.
- A sentence is true or false in a model (a domain plus an interpretation of the symbols); entailment means truth in
  every model of the knowledge base, and there are infinitely many models, so reasoning must be by inference.
- Unification finds the most general substitution that makes two expressions equal; it halts, it is correct, and the
  occurs check is what keeps it sound.
- Generalized modus ponens powers forward chaining (a terminating, polynomial fixed point for Datalog) and backward
  chaining (depth-first SLD resolution, the engine of Prolog, which can loop and answers "no" only under a closed-world
  reading).
- Clausal form with Skolem functions plus resolution and factoring is refutation-complete for all of first-order logic;
  set of support, subsumption and ordering make it practical, and superposition handles equality.
- First-order entailment is semi-decidable but undecidable (Church and Turing, 1936): proofs can be found when they
  exist, but "no" cannot always be established. Gödel's completeness theorem (about truth in all models) and his
  incompleteness theorem (about truth in the natural numbers) do not conflict.

**Next:** [Chapter 10](10-Planning.md) uses logic-based descriptions of actions to build plans: STRIPS, forward and
backward planning, heuristics from relaxed problems, GraphPlan and hierarchical planning.

## Further reading

- S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed., 2020: chapters 8 and 9 (first-order
  logic, inference, unification, chaining, resolution).
- J. A. Robinson, "A machine-oriented logic based on the resolution principle", *Journal of the ACM* 12, 1965.
- C.-L. Chang and R. C.-T. Lee, *Symbolic Logic and Mechanical Theorem Proving*, 1973 (Herbrand's theorem, the lifting
  lemma and resolution strategies, with full proofs).
- M. Davis and H. Putnam, "A computing procedure for quantification theory", *Journal of the ACM* 7, 1960.
- L. Wos, G. A. Robinson and D. F. Carson, "Efficiency and completeness of the set of support strategy in theorem
  proving", *Journal of the ACM* 12, 1965.
- M. S. Paterson and M. N. Wegman, "Linear unification", *Journal of Computer and System Sciences* 16, 1978;
  A. Martelli and U. Montanari, "An efficient unification algorithm", *ACM Transactions on Programming Languages and
  Systems* 4, 1982.
- C. Green, "Application of theorem proving to problem solving", IJCAI 1969.
- R. Kowalski, "Predicate logic as a programming language", IFIP Congress 1974; R. Kowalski, "Algorithm = logic +
  control", *Communications of the ACM* 22, 1979.
- A. Colmerauer and P. Roussel, "The birth of Prolog", in *History of Programming Languages II*, 1996.
- C. L. Forgy, "Rete: a fast algorithm for the many pattern/many object pattern match problem", *Artificial
  Intelligence* 19, 1982.
- S. Abiteboul, R. Hull and V. Vianu, *Foundations of Databases*, 1995 (Datalog, fixed points, data complexity).
- A. Church, "A note on the Entscheidungsproblem", *Journal of Symbolic Logic* 1, 1936; A. M. Turing, "On computable
  numbers, with an application to the Entscheidungsproblem", *Proceedings of the London Mathematical Society*, 1936.
- K. Gödel, "Die Vollständigkeit der Axiome des logischen Funktionenkalküls", 1930; "Über formal unentscheidbare Sätze
  der Principia Mathematica und verwandter Systeme I", 1931.
- W. McCune, "Solution of the Robbins problem", *Journal of Automated Reasoning* 19, 1997.
- On this site: the Logic book at [math.akadian.ca](https://math.akadian.ca/books/logic/), especially
  [First-order logic](https://math.akadian.ca/books/logic/10-First-Order-Logic.html),
  [Completeness and compactness](https://math.akadian.ca/books/logic/11-Completeness-and-Compactness.html),
  [Undecidability](https://math.akadian.ca/books/logic/14-Undecidability.html) and
  [Gödel's incompleteness theorems](https://math.akadian.ca/books/logic/18-Godels-Incompleteness-Theorems.html);
  the Algorithms book's [Chapter 22](../algorithms/22-NP-Completeness.md) (SAT and NP-completeness) and
  [Chapter 13](../algorithms/13-Dynamic-Programming.md) (memoization, the idea behind tabling).
