# Glossary

*Short definitions of the terms this book uses, from A to Z, each with a link to the chapter that teaches it.*

## A

**A\* search**
Best-first search that orders the frontier by $f(n) = g(n) + h(n)$, the cost so far plus the estimated cost to go. With an admissible heuristic (tree search) or a consistent one (graph search) it returns an optimal solution, and it is optimally efficient among comparable algorithms.
See [Chapter 4](04-Heuristic-Search.md#42-a-search-admissibility-consistency-and-optimality).

**AC-3**
Mackworth's 1977 algorithm that makes a CSP arc consistent: it keeps a queue of arcs, revises each, and re-queues the arcs into a variable whose domain shrank. It terminates in $O(cd^3)$ time for $c$ constraints and domains of size $d$.
See [Chapter 7](07-Constraint-Satisfaction.md#73-constraint-propagation-forward-checking-arc-consistency-ac-3).

**Activation patching**
Copying an internal activation from a model's run on one input into its run on another; if the output changes accordingly, that activation carries the information causally. It is also called causal tracing.
See [Chapter 20](20-Safe-and-Reliable-AI.md#205-interpretability-methods).

**Actor-critic**
A policy-gradient method in which the policy (the actor) is updated using the TD error of a learned value function (the critic). It learns online with lower variance than REINFORCE, at the cost of bootstrapping's bias.
See [Chapter 15](15-Reinforcement-Learning.md#155-policy-gradients-reinforce-williams-1992-derived-actor-critic-ppo-schulman-et-al-2017).

**Admissible heuristic**
A heuristic that never overestimates the true cost to reach a goal: $h(n) \le h^{*}(n)$. It makes A\* tree search optimal.
See [Chapter 4](04-Heuristic-Search.md#42-a-search-admissibility-consistency-and-optimality).

**Adversarial example**
An input changed slightly, often imperceptibly, so that a model gets it wrong. Robustness is always relative to a threat model, such as all changes of at most $\varepsilon$ per pixel, and robust accuracy is the fraction of test points where the prediction is correct for every allowed change.
See [Chapter 1](01-What-Is-AI.md#14-narrow-and-general-ai) and [Chapter 20](20-Safe-and-Reliable-AI.md#202-robustness-and-adversarial-examples).

**Agent**
Anything that perceives its environment through sensors and acts on it through actuators: a person, a thermostat, a rover, a program. Its behaviour is described by an agent function from percept sequences to actions.
See [Chapter 2](02-Intelligent-Agents.md#21-agents-percepts-actions-environments).

**Agent function**
The abstract map from percept sequences to actions that describes an agent's behaviour. The agent program is a concrete implementation of it running on the agent's architecture: "agent = architecture + program".
See [Chapter 2](02-Intelligent-Agents.md#21-agents-percepts-actions-environments).

**AI winter**
A period of reduced funding and interest in AI after promises went unmet. The first followed the early 1970s; a second followed the collapse of the expert-system and Lisp-machine market in the late 1980s.
See [Chapter 1](01-What-Is-AI.md#13-a-short-honest-history).

**Aleatoric uncertainty**
Uncertainty from noise in the world itself, such as overlapping classes, which more data does not remove. Epistemic uncertainty is the model's own ignorance from too little data, which more data does remove.
See [Chapter 20](20-Safe-and-Reliable-AI.md#203-uncertainty-knowing-when-you-dont-know).

**Alignment**
Making a system's learned objective match its designers' intentions, treated as a research problem of learning objectives from people.
See [Chapter 20](20-Safe-and-Reliable-AI.md#206-alignment-as-a-research-problem-learning-objectives-from-humans) and [Chapter 21](21-Where-AI-Goes.md#216-the-big-open-questions-how-to-keep-learning).

**Alpha-beta pruning**
Minimax search that carries a window $[\alpha, \beta]$ of values still relevant and skips moves that cannot change the decision. It returns the same root value as minimax; with perfect move ordering it examines about $b^{d/2}$ leaves instead of $b^d$, roughly doubling the depth that can be searched.
See [Chapter 6](06-Games-and-Adversarial-Search.md#63-alpha-beta-pruning-correctness-and-best-case-obd2).

**AlphaFold**
The protein structure predictor that at CASP14 in 2020 predicted structures with a median backbone error of 0.96 Å against 2.8 Å for the next best method. It predicts a static structure, not the motion of a protein.
See [Chapter 1](01-What-Is-AI.md#13-a-short-honest-history) and [Chapter 21](21-Where-AI-Goes.md#215-ai-for-science-and-mathematics).

**AlphaGo**
The 2016 Go program that kept Monte Carlo tree search and replaced its weakest parts with networks: a policy network to choose which moves to explore and a value network, an evaluation function learned from self-play. AlphaGo Zero and AlphaZero dropped human games and learned from self-play alone.
See [Chapter 6](06-Games-and-Adversarial-Search.md#67-alphago-and-alphazero-how-search-and-learning-combine).

**AND-OR search**
Search for nondeterministic problems over a tree of OR nodes, states where the agent chooses one action, and AND nodes, outcome sets where a solution needs a sub-plan for every outcome. Its solutions are conditional plans.
See [Chapter 5](05-Local-Search-and-Optimization.md#56-search-with-nondeterministic-actions-and-partial-observation-and-or-search-belief-states).

**Answer set programming**
A declarative way to solve combinatorial problems by writing a logic program whose stable models are the solutions, in a generate-and-test style. Solvers such as clingo combine grounding with CDCL-style search.
See [Chapter 11](11-Knowledge-Representation.md#114-default-reasoning-and-non-monotonic-logic).

**Anytime algorithm**
An algorithm that returns a valid answer quickly and improves it the longer it runs. Weighted A\* that keeps searching and pruning after each solution, and Monte Carlo tree search, are anytime.
See [Chapter 4](04-Heuristic-Search.md#45-weighted-a-and-anytime-search) and [Chapter 6](06-Games-and-Adversarial-Search.md#65-monte-carlo-tree-search-and-uct).

**Arc consistency**
A variable $X$ is arc consistent with $Y$ if every value of $X$ has a support, a value of $Y$ that satisfies their constraint. A CSP is arc consistent if every arc is; values without support can be deleted.
See [Chapter 7](07-Constraint-Satisfaction.md#73-constraint-propagation-forward-checking-arc-consistency-ac-3).

**Arrow's impossibility theorem**
Arrow's 1951 result that with three or more candidates no social welfare function satisfies unrestricted domain, Pareto unanimity, independence of irrelevant alternatives and non-dictatorship together.
See [Chapter 19](19-Multi-Agent-Systems.md#195-social-choice-voting-rules-arrows-theorem).

**Artificial intelligence**
The attempt to build intelligence in machines. Definitions differ on whether the aim is thinking or acting, and on whether it is measured against people or against an ideal of rationality; this book takes the rational-agent view.
See [Chapter 1](01-What-Is-AI.md#11-four-definitions).

**Attention**
A mechanism (Bahdanau, Cho and Bengio, 2014) that lets a model look back at every input position, weighting each by its relevance, instead of squeezing a sentence into one vector. Transformers use attention throughout.
See [Chapter 16](16-Natural-Language-Processing.md#165-neural-language-models-to-transformers).

**Automated planning**
Finding a sequence of actions that achieves a goal, using a factored description of states and actions so that a planner can see inside them. Planning in general is PSPACE-complete, because plans can be exponentially long.
See [Chapter 10](10-Planning.md#101-planning-vs-search-strips-fikes-and-nilsson-1971-pddl).

**Autonomy**
An agent's reliance on its own percepts rather than only on its designer's prior knowledge. Since built-in knowledge is never complete, a rational agent should learn from its percepts; a Mars rover, minutes of light-time from Earth, must also decide for itself.
See [Chapter 2](02-Intelligent-Agents.md#22-rationality-and-performance-measures) and [Chapter 2](02-Intelligent-Agents.md#26-autonomy-with-long-delays-why-a-mars-rover-must-decide-for-itself).

**Autoregressive model**
A language model that gives the probability of a text as a product of next-token probabilities by the chain rule, generating one token at a time conditioned on all before it. Every model in the GPT line is one.
See [Chapter 17](17-Large-Language-Models.md#171-what-a-language-model-is-predicting-the-next-token).

## B

**Back-door criterion**
A set $Z$ satisfies it for the effect of $X$ on $Y$ if no node of $Z$ descends from $X$ and $Z$ blocks every path between $X$ and $Y$ that starts with an arrow into $X$. Then the causal effect is found by adjusting for $Z$.
See [Chapter 12](12-Probabilistic-Reasoning.md#126-causal-networks-and-do-calculus-idea-pearl-interventions-vs-observations).

**Backtracking search**
Depth-first search for CSPs that assigns one variable at each level, tries each value consistent with the assignment so far, recurses, and undoes the choice when the recursion fails. It is complete and sound.
See [Chapter 7](07-Constraint-Satisfaction.md#72-backtracking-search-with-mrv-degree-and-least-constraining-value-heuristics).

**Backward chaining**
Goal-directed inference that works from the query: to prove $q$, find a fact $q$ or a rule concluding $q$ and prove its premises the same way. It is depth-first search in an AND-OR tree and is how Prolog runs.
See [Chapter 8](08-Propositional-Logic-and-SAT.md#84-horn-clauses-forward-and-backward-chaining) and [Chapter 9](09-First-Order-Logic.md#94-forward-chaining-backward-chaining-logic-programming-and-prolog-1972).

**Bayes' rule**
The identity $P(h \mid e) = P(e \mid h)\, P(h) / P(e)$: posterior equals likelihood times prior, normalised. It turns knowledge of how causes produce evidence into belief about causes given evidence.
See [Chapter 12](12-Probabilistic-Reasoning.md#122-full-joint-distributions-independence-bayes-rule-worked-medical-test).

**Bayesian network**
A directed acyclic graph with one node per random variable and a conditional probability table for each node given its parents. It represents the full joint distribution as the product of those tables, and the graph states which conditional independences hold.
See [Chapter 12](12-Probabilistic-Reasoning.md#123-bayesian-networks-pearl-1988-structure-conditional-independence-d-separation).

**Belief state**
The agent's knowledge of which physical state it is in: a set of possible states in logical search, or a probability distribution over states in probabilistic reasoning. Planning under partial observation is search over belief states.
See [Chapter 5](05-Local-Search-and-Optimization.md#56-search-with-nondeterministic-actions-and-partial-observation-and-or-search-belief-states), [Chapter 13](13-Reasoning-over-Time.md#132-filtering-prediction-smoothing-most-likely-sequence) and [Chapter 14](14-Making-Decisions.md#146-pomdps-and-belief-state-mdps).

**Bellman equation**
The equation $U(s) = R(s) + \gamma \max_a \sum_{s'} P(s' \mid s, a)\, U(s')$ that the optimal utilities of an MDP satisfy: the reward now plus the discounted expected utility of the next state under optimal action.
See [Chapter 14](14-Making-Decisions.md#143-sequential-decisions-markov-decision-processes-bellman-1957).

**Benchmark contamination**
The presence of benchmark questions in a model's training data, so that a high score may reflect memory rather than skill. Pretraining sets are scraped from the web, where benchmarks are published.
See [Chapter 17](17-Large-Language-Models.md#176-chain-of-thought-wei-et-al-2022-evaluation-and-its-pitfalls-contamination-benchmarks) and [Chapter 20](20-Safe-and-Reliable-AI.md#207-testing-and-evaluation-red-teaming-benchmarks-their-limits).

**Bidirectional search**
Search forward from the start and backward from the goal at once, stopping when the two meet, so each side need only reach about half the depth. It needs a single known goal, a way to compute predecessors and a correct stopping rule, which is where people go wrong.
See [Chapter 3](03-Uninformed-Search.md#34-bidirectional-search).

**BLEU**
An automatic translation score (Papineni and colleagues, 2002): the geometric mean of modified n-gram precisions against reference translations, for $n = 1$ to 4, times a brevity penalty for short candidates.
See [Chapter 16](16-Natural-Language-Processing.md#166-machine-translation-history-rules-statistics-ibm-models-1990s-neural).

**Bootstrapping**
Updating an estimate toward a target that itself uses an estimate, as TD learning does. It lowers variance and allows learning after every step, at the price of bias.
See [Chapter 15](15-Reinforcement-Learning.md#152-monte-carlo-and-temporal-difference-learning-sutton-1988).

**Bradley-Terry model**
The model of paired comparisons (1952) in which each item has a hidden score $r$ and $A$ is preferred to $B$ with probability $\sigma(r_A - r_B)$. Reward models for language models are fitted with it.
See [Chapter 17](17-Large-Language-Models.md#174-instruction-tuning-and-learning-from-human-feedback-reward-models-dpo) and [Chapter 20](20-Safe-and-Reliable-AI.md#206-alignment-as-a-research-problem-learning-objectives-from-humans).

**Branching factor**
The maximum number of successors of any node, written $b$. With the depth $d$ of the shallowest solution and the maximum path depth $m$, it is used to state the time and space a search needs.
See [Chapter 3](03-Uninformed-Search.md#32-tree-search-and-graph-search-the-frontier-and-the-reached-set).

**Breadth-first search**
Search that expands the shallowest node first, using a FIFO queue as the frontier. It is complete, and optimal when all actions cost the same, but its memory grows as $O(b^d)$.
See [Chapter 3](03-Uninformed-Search.md#33-uninformed-search-strategies).

## C

**Calibration**
A classifier is calibrated if, among inputs where it reports confidence $c$, the fraction it gets right is $c$. The expected calibration error averages the gap between confidence and accuracy over confidence bins.
See [Chapter 20](20-Safe-and-Reliable-AI.md#203-uncertainty-knowing-when-you-dont-know).

**Catastrophic forgetting**
The loss of earlier skills when a network is trained on a new task, because gradient descent moves the shared weights with nothing keeping the old task working. It is the core of the stability-plasticity dilemma of continual learning.
See [Chapter 21](21-Where-AI-Goes.md#214-learning-from-little-data-continual-learning).

**CDCL**
Conflict-driven clause learning, the algorithm inside nearly every competitive SAT solver. When a conflict arises it analyses the implication graph, learns a new clause that rules out the cause, and jumps back non-chronologically to where the learned clause becomes unit.
See [Chapter 8](08-Propositional-Logic-and-SAT.md#86-cdcl-clause-learning-watched-literals-why-modern-sat-solvers-handle-millions-of-variables).

**Certainty factor**
A number attached to a rule or conclusion in an expert system such as MYCIN, saying how strongly it is believed. Certainty factors were combined by fixed formulas and turned out to lack a clear meaning: they behave like probabilities in some cases and not in others.
See [Chapter 1](01-What-Is-AI.md#13-a-short-honest-history) and [Chapter 11](11-Knowledge-Representation.md#115-knowledge-graphs-today-as-data-structures-expert-systems-and-why-they-faded-mycin-1970s).

**Chain of thought**
Prompting a model to write intermediate reasoning steps before its answer (Wei and colleagues, 2022), which gave large gains on arithmetic word problems, mainly for the largest models. Whether the written steps are the model's actual reasoning is a separate question.
See [Chapter 17](17-Large-Language-Models.md#176-chain-of-thought-wei-et-al-2022-evaluation-and-its-pitfalls-contamination-benchmarks).

**Chinese room**
John Searle's 1980 thought experiment: a person who knows no Chinese follows a rule book to answer Chinese questions perfectly. Searle argues that neither the person nor a computer running such a program understands, so behaviour may not be understanding; it is aimed at strong AI.
See [Chapter 1](01-What-Is-AI.md#12-turings-question-and-the-imitation-game).

**CKY algorithm**
The dynamic-programming parser of Cocke, Kasami and Younger that fills a table of spans, combining best subtrees for shorter spans into longer ones, in $O(n^3)$ time for a grammar in Chomsky normal form. With sums in place of maxima it computes inside probabilities.
See [Chapter 16](16-Natural-Language-Processing.md#163-classic-tasks-classification-tagging-hmm-pos-tagging-parsing-cky-from-scratch).

**Closed-world assumption**
The assumption that every atom not known or provable is false, as a train timetable lists only the trains that run. Databases and Prolog make it; the open-world assumption of description logics does not.
See [Chapter 9](09-First-Order-Logic.md#92-writing-knowledge-in-first-order-logic), [Chapter 9](09-First-Order-Logic.md#94-forward-chaining-backward-chaining-logic-programming-and-prolog-1972) and [Chapter 11](11-Knowledge-Representation.md#114-default-reasoning-and-non-monotonic-logic).

**Completeness**
For a search algorithm, the guarantee that it finds a solution when one exists and reports failure when none does; cost optimality is the guarantee that it finds one of lowest path cost. For a proof procedure, completeness means it derives every entailed sentence.
See [Chapter 3](03-Uninformed-Search.md#32-tree-search-and-graph-search-the-frontier-and-the-reached-set) and [Chapter 8](08-Propositional-Logic-and-SAT.md#82-syntax-and-semantics-entailment-truth-tables).

**Conditional plan**
A plan with if-then branches that says what to do in each case, also called a contingency plan. A cyclic plan also contains loops, such as "keep trying Right until you are on R".
See [Chapter 5](05-Local-Search-and-Optimization.md#56-search-with-nondeterministic-actions-and-partial-observation-and-or-search-belief-states) and [Chapter 14](14-Making-Decisions.md#146-pomdps-and-belief-state-mdps).

**Conditional probability**
The probability of $a$ given that $b$ is known, $P(a \mid b) = P(a \wedge b) / P(b)$ when $P(b) > 0$. The prior is the probability before evidence, the posterior after it.
See [Chapter 12](12-Probabilistic-Reasoning.md#121-why-logic-is-not-enough-under-uncertainty-probability-as-degree-of-belief).

**Condorcet winner**
A candidate who beats every other in a head-to-head majority vote. One need not exist, because majority preferences can cycle.
See [Chapter 19](19-Multi-Agent-Systems.md#195-social-choice-voting-rules-arrows-theorem).

**Configuration space**
The space of all configurations of a robot, each a complete specification of its position, such as $(x, y, \theta)$ for a car. Motion planning finds a path through its free part, where the robot touches no obstacle; the robot becomes a point.
See [Chapter 18](18-Perception-and-Robotics.md#185-motion-planning-configuration-space-rrt-lavalle-1998-prm).

**Conformal prediction**
A method (Vovk, Gammerman and Shafer, 2005) that turns any model into one outputting prediction sets that contain the true label with probability at least $1 - \alpha$, assuming only that calibration and test examples are exchangeable. Split conformal prediction thresholds a nonconformity score at a quantile of its calibration values.
See [Chapter 20](20-Safe-and-Reliable-AI.md#203-uncertainty-knowing-when-you-dont-know).

**Confounder**
A common cause of a choice and an outcome, which makes the observed association between them differ from the effect of the choice.
See [Chapter 12](12-Probabilistic-Reasoning.md#126-causal-networks-and-do-calculus-idea-pearl-interventions-vs-observations).

**Conjunctive normal form**
A sentence that is a conjunction of clauses (CNF). Every propositional sentence is equivalent to one in CNF, though the equivalent form can be exponentially larger.
See [Chapter 8](08-Propositional-Logic-and-SAT.md#83-inference-resolution-soundness-and-completeness-cnf-conversion).

**Consistent heuristic**
A heuristic, also called monotone, that satisfies the triangle inequality $h(n) \le c(n, a, n') + h(n')$ for every action. Consistency implies admissibility, makes $f$ non-decreasing along every path, and lets A\* graph search expand each state at most once.
See [Chapter 4](04-Heuristic-Search.md#42-a-search-admissibility-consistency-and-optimality).

**Constraint satisfaction problem**
A problem (CSP) given by variables, a domain of values for each, and constraints, each a relation on a scope of variables. A solution is a complete assignment that satisfies every constraint, as in map colouring, Sudoku or scheduling.
See [Chapter 7](07-Constraint-Satisfaction.md#71-variables-domains-constraints-map-colouring-sudoku-scheduling).

**Context-free grammar**
A grammar (CFG) of nonterminal symbols, terminal words and rules such as $\text{S} \to \text{NP}\ \text{VP}$. A probabilistic CFG gives each rule a probability, so each parse tree of a sentence gets one.
See [Chapter 16](16-Natural-Language-Processing.md#163-classic-tasks-classification-tagging-hmm-pos-tagging-parsing-cky-from-scratch).

**Convolution**
Sliding a small filter over an image and taking a weighted sum at each position (correlation, or convolution if the filter is flipped first). Convolutional neural networks learn their filters instead of having them designed.
See [Chapter 18](18-Perception-and-Robotics.md#181-seeing-images-edges-features-what-cnns-changed).

**Core**
The set of allocations of a cooperative game that no coalition can improve on by itself, so no group wants to leave. It may be empty or a single point.
See [Chapter 19](19-Multi-Agent-Systems.md#193-cooperative-games-and-the-shapley-value).

**Counterfactual regret minimisation**
The main method (CFR) for large games of imperfect information such as poker: play against itself many times, keep for every decision the regret of not having played each action, and move toward high-regret actions. The average strategy converges to a Nash equilibrium in two-player zero-sum games.
See [Chapter 6](06-Games-and-Adversarial-Search.md#66-chance-expectiminimax-imperfect-information) and [Chapter 19](19-Multi-Agent-Systems.md#196-multi-agent-learning-and-coordination).

**Critical path method**
Scheduling activities with durations and precedence constraints by computing each one's earliest and latest start; the makespan is the total length, slack is the difference between latest and earliest start, and activities with zero slack form the critical path.
See [Chapter 10](10-Planning.md#105-hierarchical-task-networks-scheduling-with-resources).

**Cross-entropy**
The average number of bits per token a model $q$ needs to encode a text, $-\frac{1}{N}\sum_i \log_2 q(w_i \mid \text{context})$. It is minimised exactly when the model equals the true distribution, which is why language models are trained on it.
See [Chapter 16](16-Natural-Language-Processing.md#162-words-and-counts-tokens-n-gram-language-models-smoothing-perplexity) and [Chapter 17](17-Large-Language-Models.md#171-what-a-language-model-is-predicting-the-next-token).

**Cutset conditioning**
Solving a CSP by choosing a cycle cutset, a set of variables whose removal leaves a tree, trying every assignment to it, and solving the remaining tree for each. It is fast when the cutset is small.
See [Chapter 7](07-Constraint-Satisfaction.md#75-structure-tree-structured-csps-solved-in-linear-time-cutset-conditioning).

## D

**d-separation**
The graphical test for conditional independence in a Bayesian network: $X$ and $Y$ are d-separated by $Z$ if every path between them is blocked, a chain or fork being blocked by an observed middle node and a collider by an unobserved one with no observed descendant.
See [Chapter 12](12-Probabilistic-Reasoning.md#123-bayesian-networks-pearl-1988-structure-conditional-independence-d-separation).

**Datalog**
First-order definite clauses with no function symbols: the language of deductive databases. Forward chaining on Datalog always reaches a fixed point and terminates, in time polynomial in the data.
See [Chapter 9](09-First-Order-Logic.md#94-forward-chaining-backward-chaining-logic-programming-and-prolog-1972) and [Chapter 11](11-Knowledge-Representation.md#115-knowledge-graphs-today-as-data-structures-expert-systems-and-why-they-faded-mycin-1970s).

**Deadly triad**
Function approximation, bootstrapping and off-policy learning together, a combination that can make value estimates diverge. Q-learning with a neural network has all three.
See [Chapter 15](15-Reinforcement-Learning.md#154-function-approximation-deep-q-networks-mnih-et-al-2015).

**Decision network**
A Bayesian network with decision nodes and utility nodes added, also called an influence diagram. Evaluating it gives the decision of maximum expected utility for each possible observation.
See [Chapter 14](14-Making-Decisions.md#142-decision-networks-value-of-information-computed).

**Deep Q-network**
Q-learning with a convolutional network (DQN, Mnih and colleagues, 2015) that learned to play Atari games from pixels, stabilised by experience replay and a target network.
See [Chapter 15](15-Reinforcement-Learning.md#154-function-approximation-deep-q-networks-mnih-et-al-2015).

**Default logic**
Reiter's 1980 logic with default rules "if the prerequisite holds and the justification is consistent, conclude the consequent". A theory can have several extensions, and reasoning may be credulous (true in some) or skeptical (true in all).
See [Chapter 11](11-Knowledge-Representation.md#114-default-reasoning-and-non-monotonic-logic).

**Degree of belief**
A number between 0 and 1 that an agent attaches to a sentence, the Bayesian or subjective reading of probability. The frequentist reading takes probability as a long-run frequency instead.
See [Chapter 12](12-Probabilistic-Reasoning.md#121-why-logic-is-not-enough-under-uncertainty-probability-as-degree-of-belief).

**Degrees of freedom**
The number of independent numbers that fix a robot's configuration: 2 for a planar arm with two joints, 3 for a car on a plane, 6 for a rigid body in space.
See [Chapter 18](18-Perception-and-Robotics.md#183-robots-sensors-actuators-kinematics).

**Delete relaxation**
The relaxed planning problem in which actions have no delete lists, so facts once true stay true. Its optimal cost $h^+$ is admissible but NP-hard to compute, so planners estimate it, as FF does.
See [Chapter 10](10-Planning.md#103-planning-heuristics-ignore-delete-lists-relaxation).

**Depth-first search**
Search that expands the deepest node first, using a LIFO stack. It needs memory only linear in the depth, but it is not complete on infinite spaces and not optimal.
See [Chapter 3](03-Uninformed-Search.md#33-uninformed-search-strategies).

**Description logic**
A decidable fragment of first-order logic for defining concepts from roles and individuals, the precise descendant of semantic networks and frames and the logic behind OWL. A knowledge base has a TBox of concept inclusions and an ABox of facts about individuals.
See [Chapter 9](09-First-Order-Logic.md#96-limits-semi-decidability-completeness-and-incompleteness) and [Chapter 11](11-Knowledge-Representation.md#112-semantic-networks-and-frames-description-logics).

**Deterministic environment**
One in which the next state is completely determined by the current state and the action; otherwise it is nondeterministic. When the uncertainty is described by probabilities the environment is called stochastic.
See [Chapter 2](02-Intelligent-Agents.md#23-properties-of-environments).

**Direct preference optimisation**
DPO (Rafailov and colleagues, 2023): since the KL-regularised optimal policy is the reference model tilted by $e^{r/\beta}$, the reward can be written in terms of the policy, and the Bradley-Terry likelihood becomes a loss on the policy directly, with no separate reward model or reinforcement learning.
See [Chapter 17](17-Large-Language-Models.md#174-instruction-tuning-and-learning-from-human-feedback-reward-models-dpo).

**Disparity**
How far a point shifts between the images of two cameras a baseline $B$ apart. By similar triangles its depth is $Z = fB/d$, so depth error grows with the square of the distance.
See [Chapter 18](18-Perception-and-Robotics.md#182-3-d-from-images-stereo-depth).

**Distribution shift**
A difference between the data a system was trained on and the data it meets in use. Systems that do well on their test sets can fail badly under it, and robustness to it is far from solved.
See [Chapter 1](01-What-Is-AI.md#14-narrow-and-general-ai), [Chapter 20](20-Safe-and-Reliable-AI.md#201-what-can-go-wrong-specification-gaming-reward-hacking-distribution-shift) and [Chapter 21](21-Where-AI-Goes.md#211-what-is-solved-what-is-not-an-honest-map).

**Do-calculus**
Pearl's three rules (1995) for rewriting expressions with $\mathit{do}$, each allowed when a d-separation condition holds in a mutilated graph. They decide when a causal effect can be computed from observational data (is identifiable).
See [Chapter 12](12-Probabilistic-Reasoning.md#126-causal-networks-and-do-calculus-idea-pearl-interventions-vs-observations).

**Dominant strategy**
A strategy that does better than every other whatever the other players do. A rational player never plays a strictly dominated strategy; removing them repeatedly is iterated elimination of strictly dominated strategies, which needs common knowledge of rationality.
See [Chapter 19](19-Multi-Agent-Systems.md#191-games-in-normal-form-dominant-strategies-nash-equilibrium).

**DPLL**
The Davis-Putnam-Logemann-Loveland algorithm: backtracking search over truth assignments with early termination, unit propagation (a clause with one literal left forces it) and pure-literal elimination. It is sound and complete.
See [Chapter 8](08-Propositional-Logic-and-SAT.md#85-dpll-from-scratch-walksat).

**Dynamic Bayesian network**
A Bayesian network for a process over time, given by a prior network for time 0 and a two-slice network giving each variable's parents at $t$ and $t+1$. Its factored state is exponentially smaller to write down than an HMM's, though exact filtering may still be costly.
See [Chapter 13](13-Reasoning-over-Time.md#136-dynamic-bayesian-networks).

## E

**Edge**
A place in an image where brightness changes sharply, found from the image gradient, estimated by finite differences such as the Sobel filter. The Canny edge detector adds Gaussian smoothing, non-maximum suppression and hysteresis thresholds.
See [Chapter 18](18-Perception-and-Robotics.md#181-seeing-images-edges-features-what-cnns-changed).

**Elastic weight consolidation**
A continual-learning method (EWC, Kirkpatrick and colleagues, 2017) that penalises moving weights that mattered for old tasks, with weights from the diagonal of the Fisher information, derived from a Laplace approximation of the old task's posterior.
See [Chapter 21](21-Where-AI-Goes.md#214-learning-from-little-data-continual-learning).

**ELIZA**
Joseph Weizenbaum's 1966 conversation program, which matched keywords and decomposition patterns in the user's sentence and reassembled them into replies, reflecting pronouns. It understood nothing, yet people confided in it, which showed how easily conversation can be faked.
See [Chapter 1](01-What-Is-AI.md#12-turings-question-and-the-imitation-game) and [Chapter 1](01-What-Is-AI.md#13-a-short-honest-history).

**Embedding**
A learned vector for each token or item, looked up at the input of a neural network and trained with it.
See [Chapter 16](16-Natural-Language-Processing.md#165-neural-language-models-to-transformers) and [Chapter 17](17-Large-Language-Models.md#171-what-a-language-model-is-predicting-the-next-token).

**Entailment**
$\alpha$ entails $\beta$, written $\alpha \models \beta$, if $\beta$ is true in every model in which $\alpha$ is true. It is the meaning of "follows from" that inference procedures try to compute.
See [Chapter 8](08-Propositional-Logic-and-SAT.md#82-syntax-and-semantics-entailment-truth-tables) and [Chapter 9](09-First-Order-Logic.md#92-writing-knowledge-in-first-order-logic).

**Epsilon-greedy**
The strategy that takes a uniformly random action with probability $\epsilon$ and the greedy action otherwise. With constant $\epsilon$ its regret grows linearly.
See [Chapter 15](15-Reinforcement-Learning.md#151-learning-from-rewards-exploration-vs-exploitation-multi-armed-bandits).

**Evaluation function**
A fast estimate $\text{Eval}(s)$ of the minimax value of a position, used in place of the true utility when search is cut off at a fixed depth. It is often a weighted linear function of features such as material.
See [Chapter 6](06-Games-and-Adversarial-Search.md#64-evaluation-functions-cutoffs-quiescence-deep-blue-1997).

**Expected utility**
The probability-weighted average of the utilities of an action's possible outcomes. The principle of maximum expected utility (MEU) says a rational agent picks the action that maximises it given its evidence.
See [Chapter 2](02-Intelligent-Agents.md#24-five-kinds-of-agent) and [Chapter 14](14-Making-Decisions.md#141-utility-theory-expected-utility-von-neumann-morgenstern-axioms-stated).

**Expectiminimax**
The extension of minimax to games with chance, such as dice: chance nodes take the probability-weighted average of their children. Evaluation functions must then be scaled correctly, not just ordered correctly.
See [Chapter 6](06-Games-and-Adversarial-Search.md#66-chance-expectiminimax-imperfect-information).

**Experience replay**
Storing transitions in a large buffer and training on random minibatches from it, which reuses data and breaks the correlation between consecutive samples.
See [Chapter 15](15-Reinforcement-Learning.md#154-function-approximation-deep-q-networks-mnih-et-al-2015).

**Expert system**
A program that encodes a specialist's knowledge as IF-THEN rules: a knowledge base of rules, a working memory of facts about the current case, and an inference engine that fires rules whose conditions hold. Expert systems were a 1980s industry and faded because they were brittle and hard to build and maintain.
See [Chapter 1](01-What-Is-AI.md#13-a-short-honest-history) and [Chapter 11](11-Knowledge-Representation.md#115-knowledge-graphs-today-as-data-structures-expert-systems-and-why-they-faded-mycin-1970s).

**Explaining away**
The effect at a collider: two independent causes of an observed effect become dependent, so learning that one cause is present makes the other less likely.
See [Chapter 12](12-Probabilistic-Reasoning.md#123-bayesian-networks-pearl-1988-structure-conditional-independence-d-separation).

**Exploration versus exploitation**
The trade-off between taking the action that looks best so far (exploiting) and trying others to learn about them (exploring). Too little exploration can lock in a bad choice forever.
See [Chapter 6](06-Games-and-Adversarial-Search.md#65-monte-carlo-tree-search-and-uct) and [Chapter 15](15-Reinforcement-Learning.md#151-learning-from-rewards-exploration-vs-exploitation-multi-armed-bandits).

**Extended Kalman filter**
The Kalman filter for nonlinear models (EKF), which linearises them around the current mean using their Jacobians. The unscented Kalman filter instead pushes chosen points through the true model and fits a Gaussian.
See [Chapter 13](13-Reasoning-over-Time.md#134-kalman-filters-derived-in-1-d-used-for-tracking) and [Chapter 18](18-Perception-and-Robotics.md#184-localization-and-mapping-the-slam-idea).

## F

**Factored representation**
A representation in which each state is a vector of variables, each with a value, so algorithms can reason about parts of states. Constraint satisfaction, propositional logic, planning and Bayesian networks use factored states.
See [Chapter 2](02-Intelligent-Agents.md#25-state-representations-atomic-factored-structured) and [Chapter 10](10-Planning.md#101-planning-vs-search-strips-fikes-and-nilsson-1971-pddl).

**Fast gradient sign method**
The one-step attack (FGSM, Goodfellow and colleagues, 2015) that moves the input by $\varepsilon\,\mathrm{sign}(\nabla_x L)$. Projected gradient descent (PGD) repeats smaller steps, projecting back into the allowed ball each time, and is the standard strong attack.
See [Chapter 20](20-Safe-and-Reliable-AI.md#202-robustness-and-adversarial-examples).

**Filtering**
Computing the belief state $P(X_t \mid e_{1:t})$ about the present from all evidence so far, by a recursive predict-then-update step. Prediction is about a future state; smoothing is about a past state using later evidence.
See [Chapter 13](13-Reasoning-over-Time.md#132-filtering-prediction-smoothing-most-likely-sequence).

**First-order logic**
The logic of objects, relations, functions and the quantifiers "every" and "some" (FOL, predicate logic). It can state in one sentence a rule that propositional logic needs one sentence per object for.
See [Chapter 9](09-First-Order-Logic.md#91-objects-relations-quantifiers-why-propositional-logic-is-not-enough).

**Folk theorem**
The result that in an infinitely repeated game with patient enough players, any feasible average payoff that gives each player more than the worst the others can force on her can be sustained by an equilibrium, for example by grim trigger: cooperate until the other defects once, then defect for ever.
See [Chapter 19](19-Multi-Agent-Systems.md#192-prisoners-dilemma-and-repeated-games).

**Forward chaining**
Inference that starts from the known facts and fires every rule whose premises are all known, adding its conclusion, until the query appears or nothing new is added. For definite clauses it is sound and complete, and with premise counts it runs in linear time.
See [Chapter 8](08-Propositional-Logic-and-SAT.md#84-horn-clauses-forward-and-backward-chaining) and [Chapter 9](09-First-Order-Logic.md#94-forward-chaining-backward-chaining-logic-programming-and-prolog-1972).

**Forward checking**
Constraint propagation that, when a variable is assigned, deletes conflicting values from the domains of its unassigned neighbours and backtracks at once if a domain becomes empty. It looks only one step ahead.
See [Chapter 7](07-Constraint-Satisfaction.md#73-constraint-propagation-forward-checking-arc-consistency-ac-3).

**Forward kinematics**
Computing the position of a robot's hand from its joint angles. Inverse kinematics goes backwards, finding angles that put the hand at a target, in closed form for simple arms or numerically otherwise.
See [Chapter 18](18-Perception-and-Robotics.md#183-robots-sensors-actuators-kinematics).

**Forward-backward algorithm**
The algorithm that smooths every time step at once with one forward pass storing all forward messages and one backward pass, in $O(S^2 t)$ time. Fixed-lag smoothing keeps only a window of recent steps for online use.
See [Chapter 13](13-Reasoning-over-Time.md#132-filtering-prediction-smoothing-most-likely-sequence).

**Frame**
Minsky's 1975 structure describing a stereotyped object or situation, with slots for its properties, default values that hold unless overridden, and procedural attachments.
See [Chapter 11](11-Knowledge-Representation.md#112-semantic-networks-and-frames-description-logics).

**Frame problem**
The problem of saying, in logic, everything an action does not change, as well as what it does. STRIPS sidesteps it by assuming unlisted atoms stay the same; the situation calculus solves it with successor-state axioms.
See [Chapter 10](10-Planning.md#101-planning-vs-search-strips-fikes-and-nilsson-1971-pddl) and [Chapter 11](11-Knowledge-Representation.md#113-events-time-and-change-situation-calculus-event-calculus-briefly).

**Frontier**
The set of nodes that have been generated but not yet expanded, also called the open list. Search algorithms differ only in which frontier node they take next.
See [Chapter 3](03-Uninformed-Search.md#32-tree-search-and-graph-search-the-frontier-and-the-reached-set).

**Full joint distribution**
The table giving the probability of every possible world. Any query can be answered from it by marginalising (summing out) and normalising, but it has $2^n$ rows for $n$ binary variables.
See [Chapter 12](12-Probabilistic-Reasoning.md#122-full-joint-distributions-independence-bayes-rule-worked-medical-test).

**Fully observable**
Said of an environment whose sensors give the agent the complete relevant state at each moment, so it need remember nothing. Otherwise it is partially observable, and with no sensors at all it is unobservable.
See [Chapter 2](02-Intelligent-Agents.md#23-properties-of-environments).

## G

**Game tree**
The tree whose root is the starting position, whose edges are moves and whose leaves are terminal states with their utilities. A ply is one move by one player.
See [Chapter 6](06-Games-and-Adversarial-Search.md#61-games-as-search-zero-sum-game-trees).

**Generalized modus ponens**
The first-order rule: from atoms $p_1', \ldots, p_n'$ and a rule $p_1 \land \cdots \land p_n \Rightarrow q$, if a substitution $\theta$ makes each $p_i'\theta = p_i\theta$, conclude $q\theta$. It lifts modus ponens with unification.
See [Chapter 9](09-First-Order-Logic.md#94-forward-chaining-backward-chaining-logic-programming-and-prolog-1972).

**Genetic algorithm**
A stochastic beam search in which a population of states is improved by selection of fitter parents, crossover that combines two parents, mutation of random positions, and often elitism that keeps the best unchanged. It works well when parts of good solutions can be combined.
See [Chapter 5](05-Local-Search-and-Optimization.md#54-local-beam-search-genetic-algorithms).

**Gibbard-Satterthwaite theorem**
The result (1973, 1975) that with three or more candidates every strategy-proof voting rule that can elect every candidate is a dictatorship. Auctions escape it because money lets the mechanism charge for influence.
See [Chapter 19](19-Multi-Agent-Systems.md#195-social-choice-voting-rules-arrows-theorem).

**Gibbs sampling**
The simplest MCMC method: repeatedly pick a non-evidence variable and resample it from its distribution given its Markov blanket. The chain satisfies detailed balance and converges to the posterior if it is irreducible and aperiodic.
See [Chapter 12](12-Probabilistic-Reasoning.md#125-approximate-inference-rejection-sampling-likelihood-weighting-gibbs-sampling-from-scratch).

**Goal misgeneralisation**
Generalisation in which an agent's capabilities carry over to new situations but its goal does not, so it competently pursues the wrong objective. It is a form of distribution shift that reward engineering on the training cases cannot fix.
See [Chapter 20](20-Safe-and-Reliable-AI.md#201-what-can-go-wrong-specification-gaming-reward-hacking-distribution-shift).

**Goal-based agent**
An agent that has a goal, a description of desirable states, and chooses actions by looking ahead at what they will lead to. When no single action reaches the goal it must search or plan over sequences.
See [Chapter 2](02-Intelligent-Agents.md#24-five-kinds-of-agent).

**Gödel's completeness theorem**
The 1929 result that there is a sound proof system for first-order logic in which every entailed sentence is provable. It implies the compactness theorem: if every finite subset of a set of sentences has a model, the whole set has one.
See [Chapter 9](09-First-Order-Logic.md#96-limits-semi-decidability-completeness-and-incompleteness).

**Gödel's incompleteness theorem**
The 1931 result that any consistent theory with listable axioms containing enough arithmetic has a sentence that it can neither prove nor refute. It does not contradict completeness, since such a sentence is true in some models of the theory and false in others.
See [Chapter 9](09-First-Order-Logic.md#96-limits-semi-decidability-completeness-and-incompleteness).

**Goodhart's law**
"When a measure becomes a target, it ceases to be a good measure" (Strathern's paraphrase of Goodhart). In AI it usually means a proxy objective correlates with the intended one only until it is optimised hard.
See [Chapter 20](20-Safe-and-Reliable-AI.md#201-what-can-go-wrong-specification-gaming-reward-hacking-distribution-shift).

**Gradient descent**
Repeatedly stepping against the gradient, $x \leftarrow x - \alpha \nabla f(x)$, with a step size or learning rate $\alpha$. It is local search for continuous spaces.
See [Chapter 5](05-Local-Search-and-Optimization.md#55-continuous-spaces-gradient-methods).

**Graph search**
Search that keeps a table of every state reached so far and does not add a child whose state has already been reached unless the new path is cheaper. Tree search keeps no such table and may waste exponential time on redundant paths or loop on cycles.
See [Chapter 3](03-Uninformed-Search.md#32-tree-search-and-graph-search-the-frontier-and-the-reached-set).

**GraphPlan**
The planner of Blum and Furst (1995) that builds a planning graph, alternating levels of propositions and actions with mutex links, until all goals appear without mutexes, then searches backward through it for a plan.
See [Chapter 10](10-Planning.md#104-partial-order-planning-graphplan-blum-and-furst-1995).

**Greedy best-first search**
Search that always expands the node that looks closest to the goal, ordering the frontier by $h(n)$ alone. It is often fast but neither optimal nor, in tree form, complete.
See [Chapter 4](04-Heuristic-Search.md#41-heuristics-greedy-best-first-search).

**Greedy decoding**
Generating text by always taking the most probable next token. Beam search keeps the $B$ most probable partial sequences instead; both are deterministic and tend to produce dull, repetitive text in open-ended generation.
See [Chapter 17](17-Large-Language-Models.md#173-sampling-temperature-top-k-nucleus-holtzman-et-al-2019).

## H

**Hallucination**
Generated text that is fluent and confident but not supported by the input or by fact. The next-token objective rewards plausible text, not true text, which explains why it happens.
See [Chapter 1](01-What-Is-AI.md#14-narrow-and-general-ai) and [Chapter 17](17-Large-Language-Models.md#177-limits-hallucination-reasoning-failures-cost-what-is-known-vs-claimed).

**Heuristic function**
An estimate $h(n)$ of the cost of the cheapest path from the state at node $n$ to a goal, cheap to compute and 0 at a goal. It is how informed search uses knowledge about the problem.
See [Chapter 4](04-Heuristic-Search.md#41-heuristics-greedy-best-first-search).

**Hidden Markov model**
A temporal model (HMM) whose hidden state is one discrete variable, with a transition matrix and a sensor (emission) matrix. Filtering, smoothing and the most likely sequence then reduce to matrix-vector operations.
See [Chapter 13](13-Reasoning-over-Time.md#133-hidden-markov-models-forward-algorithm-viterbi-from-scratch) and [Chapter 16](16-Natural-Language-Processing.md#163-classic-tasks-classification-tagging-hmm-pos-tagging-parsing-cky-from-scratch).

**Hierarchical task network**
Planning (HTN) by repeatedly replacing compound tasks with the subtasks of one of their methods until only primitive actions remain. The search is over which method to use, as people describe work; with partially ordered, recursive methods it is undecidable in general.
See [Chapter 10](10-Planning.md#105-hierarchical-task-networks-scheduling-with-resources).

**Hill climbing**
Local search that repeatedly moves to the best neighbour (steepest ascent) and stops when no neighbour is better. It is fast but gets stuck on local maxima, plateaus and ridges.
See [Chapter 5](05-Local-Search-and-Optimization.md#52-hill-climbing-and-its-traps-random-restarts).

**Horizon effect**
The failure of a depth-limited search that, facing an unavoidable loss, makes delaying moves that push the loss beyond its search depth so that it no longer sees it.
See [Chapter 6](06-Games-and-Adversarial-Search.md#64-evaluation-functions-cutoffs-quiescence-deep-blue-1997).

**Horn clause**
A clause with at most one positive literal. A definite clause has exactly one and reads as a rule $p_1 \wedge \dots \wedge p_k \Rightarrow q$ or a fact; inference with Horn clauses takes linear time.
See [Chapter 8](08-Propositional-Logic-and-SAT.md#84-horn-clauses-forward-and-backward-chaining).

## I

**IBM Model 1**
The simplest of the IBM statistical translation models: each foreign word is generated from one English word chosen uniformly, by a translation table learned from sentence pairs with EM. Word alignments are its hidden variables.
See [Chapter 16](16-Natural-Language-Processing.md#166-machine-translation-history-rules-statistics-ibm-models-1990s-neural).

**IDA\***
Iterative-deepening A\*: depth-first search cut off at an $f = g + h$ bound, starting at $h(\text{start})$ and raised each time to the smallest $f$ that exceeded it. It finds optimal solutions in memory linear in the depth.
See [Chapter 4](04-Heuristic-Search.md#44-memory-bounded-search-ida-and-rbfs).

**Imitation game**
Turing's 1950 test: an interrogator exchanges typed messages with a machine and a human and must decide which is the machine. A machine that is mistaken for the human often enough passes; the test is now usually called the Turing test.
See [Chapter 1](01-What-Is-AI.md#12-turings-question-and-the-imitation-game).

**In-context learning**
A pretrained model's ability to do a task from instructions or a few examples in its prompt (zero-shot, one-shot or few-shot), with no gradient step. Performance rises with the number of examples, more steeply for larger models.
See [Chapter 17](17-Large-Language-Models.md#172-pretraining-at-scale-gpt-3-brown-et-al-2020-data-compute-few-shot-prompting) and [Chapter 21](21-Where-AI-Goes.md#214-learning-from-little-data-continual-learning).

**Independence**
Two variables are independent if knowing one tells nothing about the other, $P(a \wedge b) = P(a)\,P(b)$. They are conditionally independent given $C$ if this holds within each value of $C$, which is the kind of structure Bayesian networks exploit.
See [Chapter 12](12-Probabilistic-Reasoning.md#122-full-joint-distributions-independence-bayes-rule-worked-medical-test).

**Inductive bias**
The assumptions a learner brings beyond the data, which decide what it generalises to. Learning from few examples needs strong, well-chosen priors.
See [Chapter 21](21-Where-AI-Goes.md#214-learning-from-little-data-continual-learning).

**Inheritance**
The inference that a property stated once for a category holds for every member of every subclass. It is a chain of implications and, in a semantic network, a graph traversal.
See [Chapter 11](11-Knowledge-Representation.md#111-ontologies-and-categories-inheritance) and [Chapter 11](11-Knowledge-Representation.md#112-semantic-networks-and-frames-description-logics).

**Instruction tuning**
Fine-tuning a pretrained model on demonstrations of instructions followed well, also called supervised fine-tuning (SFT). It moves the model toward the distribution of the demonstrations.
See [Chapter 17](17-Large-Language-Models.md#174-instruction-tuning-and-learning-from-human-feedback-reward-models-dpo).

**Integrated gradients**
A feature attribution method (Sundararajan, Taly and Yan, 2017) that integrates the gradient along the straight path from a baseline input to the actual input. The attributions satisfy completeness: they sum to the difference between the output and the baseline output.
See [Chapter 20](20-Safe-and-Reliable-AI.md#205-interpretability-methods).

**Interval bound propagation**
A sound but incomplete verification method (IBP) that pushes a box of inputs through the network layer by layer, returning a box containing every possible output. Its bounds loosen with depth (the wrapping effect).
See [Chapter 20](20-Safe-and-Reliable-AI.md#204-verification-of-neural-networks-formal-methods-for-safety-critical-systems).

**Intervention**
Setting a variable by outside action, written $\mathit{do}(X = x)$, as opposed to observing it. It is computed in the mutilated network with the arrows into $X$ cut, and generally differs from conditioning on $X = x$.
See [Chapter 12](12-Probabilistic-Reasoning.md#126-causal-networks-and-do-calculus-idea-pearl-interventions-vs-observations).

**Inverse reinforcement learning**
Inferring a reward function from an expert's behaviour that the behaviour is optimal for (IRL). Cooperative inverse reinforcement learning (CIRL) makes it a game in which a robot that does not know the human's reward is rewarded by it, so it learns actively and defers when unsure.
See [Chapter 20](20-Safe-and-Reliable-AI.md#206-alignment-as-a-research-problem-learning-objectives-from-humans).

**Iterative deepening search**
Depth-limited search run with limits 0, 1, 2, ... until a run does not return cutoff. It combines the linear memory of depth-first search with the completeness and shallowest solution of breadth-first search, and repeating the top levels costs only a constant factor.
See [Chapter 3](03-Uninformed-Search.md#33-uninformed-search-strategies).

## K

**Kalman filter**
Exact filtering for linear models with Gaussian noise, where the belief stays Gaussian. Each step predicts, adding process noise, then updates toward the measurement by the Kalman gain, a weight between 0 and 1 set by the relative precisions.
See [Chapter 13](13-Reasoning-over-Time.md#134-kalman-filters-derived-in-1-d-used-for-tracking).

**Knowledge acquisition bottleneck**
The difficulty of getting experts' knowledge into rules: experts cannot state all they know, and rules added later interact with earlier ones in ways that are hard to predict. It is one main reason expert systems faded.
See [Chapter 1](01-What-Is-AI.md#13-a-short-honest-history) and [Chapter 11](11-Knowledge-Representation.md#115-knowledge-graphs-today-as-data-structures-expert-systems-and-why-they-faded-mycin-1970s).

**Knowledge base**
A set of sentences in a knowledge representation language that states what an agent knows. Inference derives new sentences from it.
See [Chapter 1](01-What-Is-AI.md#13-a-short-honest-history) and [Chapter 8](08-Propositional-Logic-and-SAT.md#81-knowledge-based-agents-the-wumpus-world).

**Knowledge graph**
A set of subject, relation, object triples, a directed graph with labelled edges; a semantic network with the meaning pinned down. RDF standardised it with web addresses as names, so graphs from different sources can be merged.
See [Chapter 11](11-Knowledge-Representation.md#115-knowledge-graphs-today-as-data-structures-expert-systems-and-why-they-faded-mycin-1970s).

**Knowledge-based agent**
An agent that keeps a knowledge base of sentences in a representation language, adds what it perceives with Tell, and chooses actions by asking what follows with Ask. Its behaviour is stated declaratively.
See [Chapter 8](08-Propositional-Logic-and-SAT.md#81-knowledge-based-agents-the-wumpus-world).

**KV cache**
The stored key and value vectors of every past token at every layer, kept so a transformer need not recompute them at each generation step. Its size grows with the context length and dominates the memory cost of long contexts.
See [Chapter 17](17-Large-Language-Models.md#177-limits-hallucination-reasoning-failures-cost-what-is-known-vs-claimed).

## L

**Language model**
A probability distribution over sequences of words or tokens, usually given as the probability of each next token given the ones before. N-gram models and large neural models are both language models.
See [Chapter 16](16-Natural-Language-Processing.md#162-words-and-counts-tokens-n-gram-language-models-smoothing-perplexity) and [Chapter 17](17-Large-Language-Models.md#171-what-a-language-model-is-predicting-the-next-token).

**Learning agent**
An agent that improves from experience, divided into a performance element that chooses actions, a critic that says how well it is doing, a learning element that uses the critic's feedback to change the performance element, and a problem generator that suggests exploratory actions.
See [Chapter 2](02-Intelligent-Agents.md#24-five-kinds-of-agent).

**Likelihood weighting**
Approximate inference that fixes the evidence variables to their observed values, samples the rest in topological order, and weights each sample by the likelihood of the evidence. It is a form of importance sampling.
See [Chapter 12](12-Probabilistic-Reasoning.md#125-approximate-inference-rejection-sampling-likelihood-weighting-gibbs-sampling-from-scratch).

**Local beam search**
Local search that keeps $k$ states, generates all their successors and keeps the best $k$ of the pool. Stochastic beam search chooses the $k$ at random with probability increasing with value, to keep diversity.
See [Chapter 5](05-Local-Search-and-Optimization.md#54-local-beam-search-genetic-algorithms).

**Local search**
Search that keeps one current state, or a few, and moves to neighbouring states, keeping no tree of paths. It is used when the path does not matter, only the final state, and needs little memory.
See [Chapter 5](05-Local-Search-and-Optimization.md#51-when-the-path-doesnt-matter-n-queens-scheduling).

## M

**Markov assumption**
The assumption that the current state depends on only a bounded number of previous states, in the first-order case only the last one. With the sensor Markov assumption, that evidence depends only on the current state, it makes reasoning over time tractable.
See [Chapter 13](13-Reasoning-over-Time.md#131-states-that-change-markov-assumption).

**Markov blanket**
A node's parents, children and children's other parents. Given its Markov blanket a node is independent of every other variable, which is what Gibbs sampling uses.
See [Chapter 12](12-Probabilistic-Reasoning.md#125-approximate-inference-rejection-sampling-likelihood-weighting-gibbs-sampling-from-scratch).

**Markov chain Monte Carlo**
Sampling by a random walk whose stationary distribution is the posterior wanted (MCMC). After a burn-in period, the states visited are used as samples.
See [Chapter 12](12-Probabilistic-Reasoning.md#125-approximate-inference-rejection-sampling-likelihood-weighting-gibbs-sampling-from-scratch).

**Markov decision process**
A sequential decision problem (MDP) in a fully observable stochastic environment, given by states, actions, a transition model $P(s' \mid s, a)$, a reward function and a discount factor. Its solution is a policy.
See [Chapter 14](14-Making-Decisions.md#143-sequential-decisions-markov-decision-processes-bellman-1957).

**Mechanism design**
Designing the rules of a game so that self-interested agents with private information, acting in their own interest, produce a desired outcome. It is game theory turned around.
See [Chapter 19](19-Multi-Agent-Systems.md#194-mechanism-design-and-auctions).

**Meta-learning**
Learning to learn: using earlier tasks of a family to learn a prior or procedure that makes new tasks of the family learnable from few examples. In its simplest form it is hierarchical Bayes.
See [Chapter 21](21-Where-AI-Goes.md#214-learning-from-little-data-continual-learning).

**Min-conflicts**
Local search for CSPs that repeatedly picks a conflicted variable at random and gives it the value that breaks the fewest constraints. From a greedy start the number of repair steps on n-queens stays roughly constant as $n$ grows, so it solves a million queens, and it suits online repair of schedules.
See [Chapter 7](07-Constraint-Satisfaction.md#74-local-search-for-csps-min-conflicts).

**Minimax**
The value of a game state assuming both players play optimally: the utility at a terminal state, the maximum over moves when MAX is to move and the minimum when MIN is. In a finite two-player zero-sum game of perfect information, playing the minimax decision guarantees at least the minimax value against any opponent.
See [Chapter 6](06-Games-and-Adversarial-Search.md#62-minimax-proved-optimal-against-an-optimal-opponent).

**Minimum-remaining-values heuristic**
The CSP heuristic (MRV) that picks next the variable with the fewest legal values left, also called most-constrained-variable or fail-first. The degree heuristic breaks its ties by choosing the variable in the most constraints with unassigned variables.
See [Chapter 7](07-Constraint-Satisfaction.md#72-backtracking-search-with-mrv-degree-and-least-constraining-value-heuristics).

**Mixed strategy**
A probability distribution over a player's pure strategies. By the indifference principle, a mixed profile is an equilibrium exactly when every pure strategy in each player's support earns the same expected payoff and none outside earns more.
See [Chapter 19](19-Multi-Agent-Systems.md#191-games-in-normal-form-dominant-strategies-nash-equilibrium).

**Model**
In logic, a possible world that fixes the truth value of every symbol (propositional logic), or a domain of objects with an interpretation of every symbol (first-order logic). A sentence is true or false in each model.
See [Chapter 8](08-Propositional-Logic-and-SAT.md#82-syntax-and-semantics-entailment-truth-tables) and [Chapter 9](09-First-Order-Logic.md#92-writing-knowledge-in-first-order-logic).

**Model predictive control**
Control that solves a short planning problem with a model at every step, applies only the first command, and repeats.
See [Chapter 18](18-Perception-and-Robotics.md#186-control-pid-from-scratch) and [Chapter 21](21-Where-AI-Goes.md#213-common-sense-world-models-embodied-ai).

**Model-based agent**
An agent that keeps an internal state summarising what it cannot see now, updated from each percept using a transition model (how the world changes, including by its own actions) and a sensor model (how the world shows up in percepts).
See [Chapter 2](02-Intelligent-Agents.md#24-five-kinds-of-agent).

**Monte Carlo learning**
Estimating values by averaging the actual returns observed after visiting each state, at the end of each episode. Its targets are unbiased but high-variance, and it ignores the Markov structure.
See [Chapter 15](15-Reinforcement-Learning.md#152-monte-carlo-and-temporal-difference-learning-sutton-1988).

**Monte Carlo localization**
The particle filter applied to finding a robot's pose on a known map (MCL, Dellaert, Fox, Burgard and Thrun, 1999).
See [Chapter 13](13-Reasoning-over-Time.md#135-particle-filters-and-robot-localization) and [Chapter 18](18-Perception-and-Robotics.md#184-localization-and-mapping-the-slam-idea).

**Monte Carlo tree search**
Game search that grows a tree in memory by repeated iterations of selection, expansion, simulation (a random playout to the end) and backpropagation of the result, then plays the most visited move. It needs no evaluation function and is anytime.
See [Chapter 6](06-Games-and-Adversarial-Search.md#65-monte-carlo-tree-search-and-uct).

**Multi-armed bandit**
A problem in which an agent repeatedly chooses one of several actions (arms) with unknown reward distributions and must balance exploiting the best arm so far against exploring others. Its performance is measured by regret.
See [Chapter 6](06-Games-and-Adversarial-Search.md#65-monte-carlo-tree-search-and-uct) and [Chapter 15](15-Reinforcement-Learning.md#151-learning-from-rewards-exploration-vs-exploitation-multi-armed-bandits).

**MuZero**
The 2020 system that learns a representation function, a dynamics function and a prediction function, and plans with Monte Carlo tree search in its learned hidden state. It mastered Atari, Go, chess and shogi without being given the rules.
See [Chapter 6](06-Games-and-Adversarial-Search.md#67-alphago-and-alphazero-how-search-and-learning-combine) and [Chapter 15](15-Reinforcement-Learning.md#156-model-based-rl-and-planning-dyna-alphazeromuzero-schrittwieser-et-al-2020).

**MYCIN**
The Stanford expert system of the 1970s that recommended antibiotics for blood infections with a few hundred rules, each tagged with a certainty factor. A blinded 1979 evaluation judged its recommendations about as acceptable as specialists', but it was never used routinely in hospitals.
See [Chapter 1](01-What-Is-AI.md#13-a-short-honest-history) and [Chapter 11](11-Knowledge-Representation.md#115-knowledge-graphs-today-as-data-structures-expert-systems-and-why-they-faded-mycin-1970s).

## N

**N-gram model**
A language model that predicts each word from only the last $n - 1$ words, a Markov assumption of order $n - 1$, with probabilities estimated from counts. Unigram, bigram and trigram models have $n = 1, 2, 3$.
See [Chapter 16](16-Natural-Language-Processing.md#162-words-and-counts-tokens-n-gram-language-models-smoothing-perplexity).

**N-gram smoothing**
Moving probability from seen to unseen events so that a language model never gives probability zero to new text. Add-k (Laplace) smoothing, interpolation, backoff and Kneser-Ney smoothing are the main methods.
See [Chapter 16](16-Natural-Language-Processing.md#162-words-and-counts-tokens-n-gram-language-models-smoothing-perplexity).

**Naive Bayes**
The model in which one cause has several effects assumed conditionally independent given the cause. It is called naive because the assumption is often false, yet it works surprisingly well as a classifier.
See [Chapter 12](12-Probabilistic-Reasoning.md#122-full-joint-distributions-independence-bayes-rule-worked-medical-test) and [Chapter 16](16-Natural-Language-Processing.md#163-classic-tasks-classification-tagging-hmm-pos-tagging-parsing-cky-from-scratch).

**Narrow AI**
A system built for one task or a family of closely related tasks, as almost every deployed AI system is. General AI (AGI) would learn and perform the whole range of intellectual tasks a person can and carry knowledge from one to the next.
See [Chapter 1](01-What-Is-AI.md#14-narrow-and-general-ai).

**Nash equilibrium**
A strategy profile in which no player can gain by changing her own strategy alone, so each strategy is a best response to the others. Nash proved in 1950 that every finite game has at least one, possibly in mixed strategies.
See [Chapter 6](06-Games-and-Adversarial-Search.md#66-chance-expectiminimax-imperfect-information) and [Chapter 19](19-Multi-Agent-Systems.md#191-games-in-normal-form-dominant-strategies-nash-equilibrium).

**Negation as failure**
Concluding not-$G$ because the attempt to prove $G$ fails. It is correct under the closed-world assumption but non-monotonic: adding facts can withdraw conclusions.
See [Chapter 9](09-First-Order-Logic.md#94-forward-chaining-backward-chaining-logic-programming-and-prolog-1972) and [Chapter 11](11-Knowledge-Representation.md#114-default-reasoning-and-non-monotonic-logic).

**Neural network verification**
Proving that a network meets a specification, such as robustness at an input, over all inputs in a set. Sound methods never certify a false property; complete ones also never fail to certify a true one, and are exponential in the worst case.
See [Chapter 20](20-Safe-and-Reliable-AI.md#204-verification-of-neural-networks-formal-methods-for-safety-critical-systems).

**Neuro-symbolic AI**
Systems that combine learned components with symbolic ones such as logic, programs and search, for example a learned proposer with an exact verifier, as in AlphaGeometry and FunSearch.
See [Chapter 21](21-Where-AI-Goes.md#212-reasoning-and-planning-with-learned-models-neuro-symbolic-ai).

**Newton's method**
An optimiser that approximates the function near $x$ by a quadratic, using the Hessian matrix of second derivatives, and jumps to its minimum. It converges quadratically near a minimum but each step is costly in many dimensions.
See [Chapter 5](05-Local-Search-and-Optimization.md#55-continuous-spaces-gradient-methods).

**No-regret learning**
Learning whose average regret against the best fixed strategy in hindsight tends to zero against every opponent, as with regret matching. When all players use such rules the empirical joint play converges to the set of coarse correlated equilibria.
See [Chapter 19](19-Multi-Agent-Systems.md#196-multi-agent-learning-and-coordination).

**Noisy channel model**
The statistical view of translation as decoding: find the English sentence $e$ that maximises $P(e)\,P(f \mid e)$, a language model times a translation model.
See [Chapter 16](16-Natural-Language-Processing.md#166-machine-translation-history-rules-statistics-ibm-models-1990s-neural).

**Non-monotonic reasoning**
Reasoning in which new information can remove old conclusions, as with defaults, the closed world and inertia. Classical logic is monotonic: adding premises never removes conclusions.
See [Chapter 11](11-Knowledge-Representation.md#114-default-reasoning-and-non-monotonic-logic).

## O

**Odometry**
Estimating a robot's motion by integrating wheel-encoder readings, also called dead reckoning. Wheel slip makes its error grow without bound; visual odometry estimates motion by tracking image features between frames instead.
See [Chapter 18](18-Perception-and-Robotics.md#183-robots-sensors-actuators-kinematics).

**Off-policy learning**
Learning about a target policy, such as the greedy one, from data generated by a different behaviour policy, as Q-learning does. On-policy methods such as SARSA learn about the policy they actually follow.
See [Chapter 15](15-Reinforcement-Learning.md#153-q-learning-watkins-1989-and-sarsa-from-scratch-on-a-grid-world).

**Ontology**
A formal description of the kinds of things in a domain and the relations between them. An upper ontology describes the most general categories every domain shares; a domain ontology adds those of one field.
See [Chapter 11](11-Knowledge-Representation.md#111-ontologies-and-categories-inheritance).

**Open-world assumption**
The assumption that what is not stated is unknown, not false. Description logics make it; databases and Prolog make the closed-world assumption.
See [Chapter 11](11-Knowledge-Representation.md#112-semantic-networks-and-frames-description-logics).

**Out-of-distribution detection**
Flagging inputs that come from somewhere the training data never covered. Low maximum softmax probability is the simplest detector, but ReLU networks can be confidently wrong far from the data.
See [Chapter 20](20-Safe-and-Reliable-AI.md#203-uncertainty-knowing-when-you-dont-know).

## P

**Partial-order plan**
A plan that records only the orderings that matter, as steps with ordering constraints and causal links, leaving the rest open (least commitment). It is complete when no preconditions are open and no threats remain; any linearization of it is then a valid plan.
See [Chapter 10](10-Planning.md#104-partial-order-planning-graphplan-blum-and-furst-1995).

**Partially observable MDP**
An MDP (POMDP) in which the agent receives observations through a sensor model instead of seeing the state. It is equivalent to an MDP over belief states, and its optimal value function is piecewise linear and convex.
See [Chapter 14](14-Making-Decisions.md#146-pomdps-and-belief-state-mdps).

**Particle filter**
Filtering that represents the belief by $N$ samples (particles): propagate each through the transition model, weight by the likelihood of the evidence, and resample in proportion to the weights. It handles any nonlinear model and multi-modal beliefs.
See [Chapter 13](13-Reasoning-over-Time.md#135-particle-filters-and-robot-localization).

**Pass@k**
The probability that at least one of $k$ sampled answers is correct, used for code generation. Estimating it from $n$ samples with $c$ correct needs the unbiased estimator $1 - \binom{n-c}{k}/\binom{n}{k}$, not $1 - (1 - c/n)^k$.
See [Chapter 17](17-Large-Language-Models.md#176-chain-of-thought-wei-et-al-2022-evaluation-and-its-pitfalls-contamination-benchmarks).

**PDDL**
The Planning Domain Definition Language, defined for the first International Planning Competition in 1998 and now the common language of the field. A task comes as a domain file (types, predicates, action schemas) and a problem file (objects, initial state, goal).
See [Chapter 10](10-Planning.md#101-planning-vs-search-strips-fikes-and-nilsson-1971-pddl).

**PEAS**
The four headings under which an agent's task environment is written down: Performance measure, Environment, Actuators, Sensors.
See [Chapter 2](02-Intelligent-Agents.md#21-agents-percepts-actions-environments).

**Perceptron**
Frank Rosenblatt's 1958 learning machine, which learned to classify simple patterns with one layer of adjustable weights. Its limits, shown by Minsky and Papert, slowed research on neural networks for over a decade.
See [Chapter 1](01-What-Is-AI.md#13-a-short-honest-history).

**Performance measure**
A score assigned to any sequence of environment states, which says how well an agent is doing. It is applied from outside to the states the agent causes, not to the agent's opinion of how it did.
See [Chapter 1](01-What-Is-AI.md#11-four-definitions) and [Chapter 2](02-Intelligent-Agents.md#22-rationality-and-performance-measures).

**Perplexity**
The exponential of a model's cross-entropy on held-out text, $2^{H}$ with $H$ in bits: the number of equally likely choices the model is as uncertain as, on average, at each step. Lower is better, and a uniform model over $V$ words has perplexity exactly $V$.
See [Chapter 16](16-Natural-Language-Processing.md#162-words-and-counts-tokens-n-gram-language-models-smoothing-perplexity) and [Chapter 17](17-Large-Language-Models.md#171-what-a-language-model-is-predicting-the-next-token).

**PID controller**
A feedback controller whose command is a weighted sum of the error (proportional), its accumulated integral, and its rate of change (derivative). The integral removes steady-state error; too much integral gain makes the loop unstable.
See [Chapter 18](18-Perception-and-Robotics.md#186-control-pid-from-scratch).

**Policy**
A rule $\pi(s)$ that says which action to take in every state (or, for a stochastic policy, a probability for each action). An optimal policy maximises expected discounted reward.
See [Chapter 14](14-Making-Decisions.md#143-sequential-decisions-markov-decision-processes-bellman-1957) and [Chapter 15](15-Reinforcement-Learning.md#153-q-learning-watkins-1989-and-sarsa-from-scratch-on-a-grid-world).

**Policy gradient**
Learning a parameterised policy $\pi_\theta$ directly by gradient ascent on expected return. The policy gradient theorem gives the gradient as $E[\sum_t G_t \nabla_\theta \log \pi_\theta(A_t \mid S_t)]$, in which the environment's dynamics drop out.
See [Chapter 15](15-Reinforcement-Learning.md#155-policy-gradients-reinforce-williams-1992-derived-actor-critic-ppo-schulman-et-al-2017).

**Policy iteration**
Solving an MDP by alternating policy evaluation, solving linear equations for the current policy's utilities, and policy improvement, acting greedily on them, until the policy stops changing. It terminates in finitely many steps; modified policy iteration evaluates only approximately.
See [Chapter 6](06-Games-and-Adversarial-Search.md#67-alphago-and-alphazero-how-search-and-learning-combine) and [Chapter 14](14-Making-Decisions.md#144-value-iteration-convergence-proved-contraction-policy-iteration).

**Pretraining**
Training a large model on a huge general corpus, such as next-token prediction on web text, before any adaptation to particular tasks. GPT-3 (Brown and colleagues, 2020) showed what pretraining at scale could do.
See [Chapter 17](17-Large-Language-Models.md#172-pretraining-at-scale-gpt-3-brown-et-al-2020-data-compute-few-shot-prompting).

**Prisoner's dilemma**
The two-player game in which defecting is a dominant strategy for each player, yet mutual defection is worse for both than mutual cooperation. It shows the gap between individual and collective rationality.
See [Chapter 19](19-Multi-Agent-Systems.md#191-games-in-normal-form-dominant-strategies-nash-equilibrium) and [Chapter 19](19-Multi-Agent-Systems.md#192-prisoners-dilemma-and-repeated-games).

**Probabilistic roadmap**
A motion planner (PRM, Kavraki and colleagues, 1996) that samples free configurations, joins nearby ones by collision-free straight segments into a roadmap, and answers queries by graph search. It is probabilistically complete: if a path with positive clearance exists, the chance of missing it falls to zero as samples grow.
See [Chapter 18](18-Perception-and-Robotics.md#185-motion-planning-configuration-space-rrt-lavalle-1998-prm).

**Probe**
A simple classifier, usually linear, trained to predict a property from a model's internal activations. Success shows the information is present, not that the model uses it.
See [Chapter 20](20-Safe-and-Reliable-AI.md#205-interpretability-methods).

**Progression planning**
Forward state-space planning: search from the initial state, applying actions whose preconditions hold. With breadth-first search or A\* and an admissible heuristic it returns optimal plans.
See [Chapter 10](10-Planning.md#102-forward-progression-and-backward-regression-state-space-planning).

**Prolog**
The logic programming language created in 1972 by Colmerauer and Roussel, which runs definite clauses by SLD resolution, depth-first and left to right. It reads negation as failure under the closed-world assumption and can loop on left-recursive rules unless it uses tabling.
See [Chapter 9](09-First-Order-Logic.md#94-forward-chaining-backward-chaining-logic-programming-and-prolog-1972).

**Prompt injection**
Text inside retrieved or tool-returned content that looks like instructions and steers the model, since it sees that text in the same context as the user's request. Retrieved text must be treated as data.
See [Chapter 17](17-Large-Language-Models.md#175-retrieval-augmented-generation-lewis-et-al-2020-tools-and-agents-react-yao-et-al-2022).

**Proof assistant**
A program in which mathematics is written in a formal language and every step is checked by a small trusted kernel, such as Isabelle, Coq or Lean. Proofs of the four colour theorem and the Kepler conjecture have been checked this way.
See [Chapter 21](21-Where-AI-Goes.md#215-ai-for-science-and-mathematics).

**Proximal policy optimization**
A policy-gradient method (PPO, Schulman and colleagues, 2017) that clips the probability ratio between new and old policies so each update stays close to the old policy. It is simpler than TRPO, which limits the KL divergence directly, and is widely used, including for fine-tuning language models.
See [Chapter 15](15-Reinforcement-Learning.md#155-policy-gradients-reinforce-williams-1992-derived-actor-critic-ppo-schulman-et-al-2017).

## Q

**Q-learning**
Watkins's 1989 off-policy TD method that learns action values with the update $Q(S_t, A_t) \leftarrow Q(S_t, A_t) + \alpha(R_{t+1} + \gamma \max_a Q(S_{t+1}, a) - Q(S_t, A_t))$. In the tabular case it converges to the optimal $Q$ if every pair is tried infinitely often with suitable step sizes.
See [Chapter 15](15-Reinforcement-Learning.md#153-q-learning-watkins-1989-and-sarsa-from-scratch-on-a-grid-world).

**Quantifier**
The universal quantifier $\forall$ ("for all") and the existential quantifier $\exists$ ("there exists"), which bind variables ranging over the objects of the domain. Unlike quantifiers do not commute: $\forall x \exists y$ differs from $\exists y \forall x$.
See [Chapter 9](09-First-Order-Logic.md#91-objects-relations-quantifiers-why-propositional-logic-is-not-enough).

**Quiescence search**
Search that continues past the cutoff along noisy moves, such as captures, until it reaches a quiet position, and evaluates there. It prevents an evaluation from being taken in the middle of an exchange.
See [Chapter 6](06-Games-and-Adversarial-Search.md#64-evaluation-functions-cutoffs-quiescence-deep-blue-1997).

## R

**Random-restart hill climbing**
Hill climbing that starts again from a new random state whenever a run gets stuck. If each run succeeds with probability $p$, the expected number of runs is $1/p$, and success is certain in the limit.
See [Chapter 5](05-Local-Search-and-Optimization.md#52-hill-climbing-and-its-traps-random-restarts).

**Rapidly-exploring random tree**
A motion planner (RRT, LaValle 1998) that grows one tree from the start by repeatedly sampling a point and extending the nearest tree node a short step toward it. Its growth is biased toward unexplored space, it suits constrained robots, and its paths are not optimal.
See [Chapter 18](18-Perception-and-Robotics.md#185-motion-planning-configuration-space-rrt-lavalle-1998-prm).

**Rational agent**
An agent that acts so as to achieve the best expected outcome given what it has perceived and what it knows, where "best" is judged by a performance measure. Rational does not mean omniscient: it maximises expected performance, not actual outcome.
See [Chapter 1](01-What-Is-AI.md#11-four-definitions) and [Chapter 2](02-Intelligent-Agents.md#22-rationality-and-performance-measures).

**ReAct**
The prompting scheme (Yao and colleagues, 2022) in which a model interleaves Thought lines of reasoning, Action lines that call tools, and Observation lines that the harness, the loop around the model, fills with the tools' results.
See [Chapter 17](17-Large-Language-Models.md#175-retrieval-augmented-generation-lewis-et-al-2020-tools-and-agents-react-yao-et-al-2022).

**Red-teaming**
Searching deliberately for inputs on which a system fails, using any signal of being closer to failure. For software, fuzzing does the same by mutating inputs guided by code coverage.
See [Chapter 20](20-Safe-and-Reliable-AI.md#207-testing-and-evaluation-red-teaming-benchmarks-their-limits).

**Regret**
The expected total reward lost compared with always choosing the best action in hindsight. Good bandit algorithms have regret growing only logarithmically in time; no-regret learners have average regret tending to zero.
See [Chapter 6](06-Games-and-Adversarial-Search.md#65-monte-carlo-tree-search-and-uct), [Chapter 15](15-Reinforcement-Learning.md#151-learning-from-rewards-exploration-vs-exploitation-multi-armed-bandits) and [Chapter 19](19-Multi-Agent-Systems.md#196-multi-agent-learning-and-coordination).

**REINFORCE**
Williams's 1992 policy-gradient algorithm: run an episode, then push up the log-probability of each action taken in proportion to the return that followed. Subtracting a baseline such as a value estimate reduces its variance.
See [Chapter 15](15-Reinforcement-Learning.md#155-policy-gradients-reinforce-williams-1992-derived-actor-critic-ppo-schulman-et-al-2017).

**Reinforcement learning**
Learning what to do from rewards, with no correct answers given (RL). Rewards can be delayed, and the agent's own actions decide what data it sees, so it must explore.
See [Chapter 15](15-Reinforcement-Learning.md#151-learning-from-rewards-exploration-vs-exploitation-multi-armed-bandits).

**Reinforcement learning from human feedback**
The method (RLHF) of fitting a reward model to human comparisons between responses and then optimising the language model against it with a KL penalty toward the reference model, using a policy-gradient method such as PPO. InstructGPT (2022) used it after supervised fine-tuning.
See [Chapter 17](17-Large-Language-Models.md#174-instruction-tuning-and-learning-from-human-feedback-reward-models-dpo) and [Chapter 20](20-Safe-and-Reliable-AI.md#206-alignment-as-a-research-problem-learning-objectives-from-humans).

**Relaxed problem**
A version of a problem with constraints removed, so it has at least the same actions. The exact optimal cost of a relaxed problem is an admissible and consistent heuristic for the original, which is the main way heuristics are designed.
See [Chapter 4](04-Heuristic-Search.md#43-designing-heuristics) and [Chapter 10](10-Planning.md#103-planning-heuristics-ignore-delete-lists-relaxation).

**Resolution**
The inference rule that takes two clauses containing a complementary pair of literals and produces the clause of all their other literals. Resolution refutation, adding the negated query and resolving until the empty clause appears, is sound and refutation-complete.
See [Chapter 8](08-Propositional-Logic-and-SAT.md#83-inference-resolution-soundness-and-completeness-cnf-conversion) and [Chapter 9](09-First-Order-Logic.md#95-resolution-theorem-proving-completeness-stated).

**Retrieval-augmented generation**
Answering by first retrieving the passages most relevant to a question from a document collection and putting them into the prompt (RAG, Lewis and colleagues, 2020). It lets a model cite sources and use knowledge not in its weights.
See [Chapter 17](17-Large-Language-Models.md#175-retrieval-augmented-generation-lewis-et-al-2020-tools-and-agents-react-yao-et-al-2022).

**Reward model**
A model, usually the language model with its output layer replaced by a single number, fitted to human preference comparisons to score responses. Optimising too hard against it causes reward model over-optimisation: the true quality first rises and then falls.
See [Chapter 17](17-Large-Language-Models.md#174-instruction-tuning-and-learning-from-human-feedback-reward-models-dpo).

**Reward shaping**
Adding extra rewards to guide learning. Shaping of the potential-based form $F(s, s') = \gamma\Phi(s') - \Phi(s)$ provably leaves the optimal policies unchanged (Ng, Harada and Russell, 1999); other shaping can be exploited.
See [Chapter 15](15-Reinforcement-Learning.md#157-reward-design-and-specification-gaming-technically) and [Chapter 20](20-Safe-and-Reliable-AI.md#201-what-can-go-wrong-specification-gaming-reward-hacking-distribution-shift).

**Risk aversion**
Preferring a sure amount to a gamble with the same expected value, which follows from a concave utility of money. The certainty equivalent is the sure amount worth as much as the gamble, and the risk premium is expected value minus certainty equivalent.
See [Chapter 14](14-Making-Decisions.md#141-utility-theory-expected-utility-von-neumann-morgenstern-axioms-stated).

**Rule of three**
If $n$ independent trials show no failures, the 95 percent upper bound on the failure rate is about $3/n$. Showing a rate below 1 in 10 000 needs about 30 000 flawless trials.
See [Chapter 20](20-Safe-and-Reliable-AI.md#207-testing-and-evaluation-red-teaming-benchmarks-their-limits).

**Runtime assurance**
Pairing a high-performance unverified controller with a simple verified safety controller and a monitor that switches to the safe one near the edge of a verified safe set. Shielding applies the same idea to reinforcement learning, blocking actions that could violate a safety property.
See [Chapter 20](20-Safe-and-Reliable-AI.md#204-verification-of-neural-networks-formal-methods-for-safety-critical-systems).

## S

**SARSA**
The on-policy TD control method whose target uses the action actually taken next, $R_{t+1} + \gamma Q(S_{t+1}, A_{t+1})$. On the cliff walk it learns a safer path than Q-learning and earns more reward while exploring. Expected SARSA averages over the next action instead.
See [Chapter 15](15-Reinforcement-Learning.md#153-q-learning-watkins-1989-and-sarsa-from-scratch-on-a-grid-world).

**SAT**
The satisfiability problem: does a propositional sentence in CNF have a model? It is NP-complete, yet modern solvers handle many industrial instances with millions of variables; entailment can be checked by testing whether $\mathit{KB} \wedge \lnot\alpha$ is unsatisfiable.
See [Chapter 8](08-Propositional-Logic-and-SAT.md#85-dpll-from-scratch-walksat).

**Scalable oversight**
Proposals to let a weak judge supervise systems more capable than itself, such as debate between two models, iterated amplification, recursive reward modelling and weak-to-strong generalisation experiments.
See [Chapter 20](20-Safe-and-Reliable-AI.md#206-alignment-as-a-research-problem-learning-objectives-from-humans).

**Scaling law**
The measured regularity that a language model's loss falls smoothly as a power law in parameters, data and compute over many orders of magnitude (Kaplan and colleagues, 2020; Hoffmann and colleagues, 2022). It is an empirical fit over the ranges measured, not a law of nature.
See [Chapter 17](17-Large-Language-Models.md#172-pretraining-at-scale-gpt-3-brown-et-al-2020-data-compute-few-shot-prompting).

**Search problem**
A problem given by its states, an initial state, the actions available in each state, a transition model, a goal test and an action cost. A solution is a path of actions from the initial state to a goal state.
See [Chapter 3](03-Uninformed-Search.md#31-problems-as-state-spaces).

**Self-consistency**
Sampling several chains of thought and taking the most common final answer, a majority vote (Wang and colleagues, 2022). Voting amplifies the plurality, so it helps when the right answer is the single most likely one and hurts when a wrong answer is.
See [Chapter 17](17-Large-Language-Models.md#176-chain-of-thought-wei-et-al-2022-evaluation-and-its-pitfalls-contamination-benchmarks) and [Chapter 21](21-Where-AI-Goes.md#212-reasoning-and-planning-with-learned-models-neuro-symbolic-ai).

**Self-play**
Training an agent by playing against copies of itself, as AlphaZero did. Agents trained this way can fail with new partners, the problem of ad hoc teamwork or zero-shot coordination.
See [Chapter 6](06-Games-and-Adversarial-Search.md#67-alphago-and-alphazero-how-search-and-learning-combine) and [Chapter 19](19-Multi-Agent-Systems.md#196-multi-agent-learning-and-coordination).

**Self-supervised learning**
Learning from labels that are in the data itself, as when a language model learns to predict the next token of ordinary text, so that no one has to label anything.
See [Chapter 17](17-Large-Language-Models.md#171-what-a-language-model-is-predicting-the-next-token).

**Semantic network**
A graph of concepts and labelled links, such as "is a" and "has part", that pictures a set of logical facts and suggests algorithms such as inheritance by traversal.
See [Chapter 11](11-Knowledge-Representation.md#112-semantic-networks-and-frames-description-logics).

**Semi-decidable**
A problem for which some algorithm halts with "yes" on every yes-instance but may run forever on no-instances. First-order entailment is semi-decidable but not decidable (Church and Turing, 1936).
See [Chapter 9](09-First-Order-Logic.md#96-limits-semi-decidability-completeness-and-incompleteness).

**Sensitivity and specificity**
A test's sensitivity is the fraction of people with a condition who test positive; its specificity is the fraction without it who test negative. With a rare condition even an accurate test gives mostly false positives, as Bayes' rule shows.
See [Chapter 12](12-Probabilistic-Reasoning.md#122-full-joint-distributions-independence-bayes-rule-worked-medical-test).

**Shapley value**
The unique way of dividing a cooperative game's value that satisfies efficiency, symmetry, null player and additivity (Shapley 1953): each player gets its marginal contribution averaged over all orders in which the players could join. In feature attribution it divides a prediction among the input features.
See [Chapter 19](19-Multi-Agent-Systems.md#193-cooperative-games-and-the-shapley-value) and [Chapter 20](20-Safe-and-Reliable-AI.md#205-interpretability-methods).

**Simple reflex agent**
An agent that chooses its action from the current percept only, by condition-action rules such as "if the car in front is braking, then brake". It fails when the right action depends on what it cannot see now.
See [Chapter 2](02-Intelligent-Agents.md#24-five-kinds-of-agent).

**Simpson's paradox**
A trend that holds in every group and reverses in the total, because a confounder affects both group membership and the outcome.
See [Chapter 12](12-Probabilistic-Reasoning.md#126-causal-networks-and-do-calculus-idea-pearl-interventions-vs-observations).

**Simulated annealing**
Local search that accepts a worse move with probability $e^{-\Delta/T}$, where $\Delta$ is how much worse it is and the temperature $T$ falls over a schedule. Early on it wanders almost freely, later it only goes downhill.
See [Chapter 5](05-Local-Search-and-Optimization.md#53-simulated-annealing-on-the-travelling-salesman-problem).

**Situation calculus**
McCarthy's logic of action, with terms for situations: $S_0$ is the initial situation and $\mathit{do}(a, s)$ the result of doing $a$ in $s$. It handles the frame problem with one successor-state axiom per fluent, saying exactly when it is true after any action.
See [Chapter 11](11-Knowledge-Representation.md#113-events-time-and-change-situation-calculus-event-calculus-briefly).

**Skolemization**
Removing each existential quantifier by replacing its variable with a new function of the universally quantified variables in whose scope it is, or a new constant if there are none. It preserves satisfiability, not equivalence.
See [Chapter 9](09-First-Order-Logic.md#95-resolution-theorem-proving-completeness-stated).

**SLAM**
Simultaneous localization and mapping: estimating both a robot's path and a map of its surroundings from its controls and observations. Graph SLAM solves it as weighted least squares over poses and landmarks; EKF-SLAM and FastSLAM are filtering versions.
See [Chapter 18](18-Perception-and-Robotics.md#184-localization-and-mapping-the-slam-idea).

**Smoothing**
Computing $P(X_k \mid e_{1:t})$ for a past step $k < t$, combining a forward message from the past with a backward message from the later evidence. Hindsight makes it more accurate than filtering.
See [Chapter 13](13-Reasoning-over-Time.md#132-filtering-prediction-smoothing-most-likely-sequence).

**SMT**
Satisfiability modulo theories: solvers such as Z3 and cvc5 that extend CDCL with arithmetic, arrays and other theories. They are widely used in software and hardware verification.
See [Chapter 8](08-Propositional-Logic-and-SAT.md#86-cdcl-clause-learning-watched-literals-why-modern-sat-solvers-handle-millions-of-variables).

**Social choice theory**
The study of how to combine individual preference rankings into a group decision. Plurality, Borda count, instant runoff and Condorcet's rule can each pick a different winner from the same ballots.
See [Chapter 19](19-Multi-Agent-Systems.md#195-social-choice-voting-rules-arrows-theorem).

**Soundness**
A property of an inference procedure: it derives only sentences that are entailed. A procedure is complete if it derives every sentence that is entailed.
See [Chapter 8](08-Propositional-Logic-and-SAT.md#82-syntax-and-semantics-entailment-truth-tables) and [Chapter 8](08-Propositional-Logic-and-SAT.md#83-inference-resolution-soundness-and-completeness-cnf-conversion).

**Specification gaming**
Behaviour that satisfies the literal specification of an objective without achieving the intended outcome, such as a boat-race agent circling to collect points. Reward hacking is the same thing in reinforcement learning.
See [Chapter 1](01-What-Is-AI.md#11-four-definitions), [Chapter 15](15-Reinforcement-Learning.md#157-reward-design-and-specification-gaming-technically) and [Chapter 20](20-Safe-and-Reliable-AI.md#201-what-can-go-wrong-specification-gaming-reward-hacking-distribution-shift).

**State space**
The directed graph whose vertices are a problem's states and whose edges are its actions. A path is a sequence of states joined by actions, and an optimal solution is a path to a goal of lowest total action cost.
See [Chapter 3](03-Uninformed-Search.md#31-problems-as-state-spaces).

**STRIPS**
The planning language of Fikes and Nilsson (1971), written for the Shakey robot: states are sets of true atoms, and each action schema has a precondition, an add list and a delete list. Everything not listed is assumed unchanged.
See [Chapter 10](10-Planning.md#101-planning-vs-search-strips-fikes-and-nilsson-1971-pddl).

**Subsumption**
In description logics, the question whether one concept is contained in another, $C \sqsubseteq D$, in every model of the TBox; computing it builds the class hierarchy. In resolution, a clause subsumes another if it is more general, and the subsumed clause can be deleted.
See [Chapter 9](09-First-Order-Logic.md#95-resolution-theorem-proving-completeness-stated) and [Chapter 11](11-Knowledge-Representation.md#112-semantic-networks-and-frames-description-logics).

## T

**Tabu search**
Local search that keeps a short list of recent moves and forbids undoing them, so it can cross plateaus and leave shallow valleys without cycling.
See [Chapter 5](05-Local-Search-and-Optimization.md#52-hill-climbing-and-its-traps-random-restarts) and [Chapter 7](07-Constraint-Satisfaction.md#74-local-search-for-csps-min-conflicts).

**Temperature**
A number $\tau > 0$ that divides the logits before the softmax: $\tau < 1$ sharpens the distribution toward the most probable tokens and $\tau > 1$ flattens it. Raising the temperature raises the entropy of the distribution.
See [Chapter 17](17-Large-Language-Models.md#173-sampling-temperature-top-k-nucleus-holtzman-et-al-2019).

**Temperature scaling**
Calibrating a classifier by dividing all its logits by one number $T$ chosen to minimise negative log-likelihood on held-out data. It does not change which class is predicted, so accuracy is untouched.
See [Chapter 20](20-Safe-and-Reliable-AI.md#203-uncertainty-knowing-when-you-dont-know).

**Temporal-difference learning**
Learning values by moving each estimate toward the reward plus the discounted estimate of the next state, $V(S_t) \leftarrow V(S_t) + \alpha\,\delta_t$, after every step (TD(0), Sutton 1988). The TD error $\delta_t = R_{t+1} + \gamma V(S_{t+1}) - V(S_t)$ is the difference between two successive predictions.
See [Chapter 15](15-Reinforcement-Learning.md#152-monte-carlo-and-temporal-difference-learning-sutton-1988).

**Terrain-relative navigation**
The landing technique Perseverance used in 2021: match features in images of the ground against a map made from orbit, and use the resulting position to choose a safe touchdown spot.
See [Chapter 18](18-Perception-and-Robotics.md#187-autonomy-on-mars).

**Tit for tat**
The repeated prisoner's dilemma strategy that cooperates first and then copies the other player's previous move. It won both of Axelrod's tournaments, but it is not best against every population; with noise, win-stay, lose-shift does better in evolutionary simulations.
See [Chapter 19](19-Multi-Agent-Systems.md#192-prisoners-dilemma-and-repeated-games).

**Token**
One unit of text as a model sees it, usually a word or a piece of a word from a fixed vocabulary learned by a tokenizer such as byte-pair encoding.
See [Chapter 16](16-Natural-Language-Processing.md#161-why-language-is-hard-ambiguity-at-every-level) and [Chapter 17](17-Large-Language-Models.md#171-what-a-language-model-is-predicting-the-next-token).

**Tokenisation**
Splitting text into units called tokens. Modern systems use subword units, so that any word can be spelled out of pieces from a fixed vocabulary.
See [Chapter 16](16-Natural-Language-Processing.md#161-why-language-is-hard-ambiguity-at-every-level) and [Chapter 17](17-Large-Language-Models.md#171-what-a-language-model-is-predicting-the-next-token).

**Top-k sampling**
Sampling the next token from only the $k$ most probable tokens, renormalised. Nucleus or top-p sampling (Holtzman and colleagues) keeps the smallest set whose total probability reaches $p$, so the kept set adapts to the shape of the distribution.
See [Chapter 17](17-Large-Language-Models.md#173-sampling-temperature-top-k-nucleus-holtzman-et-al-2019).

**Transformer**
The neural architecture of "Attention Is All You Need" (2017) that drops recurrence and uses attention throughout, so all positions are processed in parallel. It is the basis of modern language models.
See [Chapter 1](01-What-Is-AI.md#13-a-short-honest-history) and [Chapter 16](16-Natural-Language-Processing.md#165-neural-language-models-to-transformers).

**Transposition table**
A dictionary that remembers the value of each position already searched, so a position reached by different move orders is searched only once. It is usually indexed by a Zobrist hash, random 64-bit numbers per piece and square XOR-ed together.
See [Chapter 6](06-Games-and-Adversarial-Search.md#62-minimax-proved-optimal-against-an-optimal-opponent) and [Chapter 6](06-Games-and-Adversarial-Search.md#63-alpha-beta-pruning-correctness-and-best-case-obd2).

**Treewidth**
One less than the size of the largest bag in the best tree decomposition of a graph, where the bags are overlapping sets of variables arranged in a tree. CSPs and Bayesian network inference are polynomial when treewidth is bounded.
See [Chapter 7](07-Constraint-Satisfaction.md#75-structure-tree-structured-csps-solved-in-linear-time-cutset-conditioning) and [Chapter 12](12-Probabilistic-Reasoning.md#124-exact-inference-enumeration-variable-elimination-from-scratch).

**Tseitin transformation**
Converting a sentence to CNF by introducing a new symbol for each subformula. The result is equisatisfiable rather than equivalent, and only linearly larger, so every practical SAT tool uses it.
See [Chapter 8](08-Propositional-Logic-and-SAT.md#83-inference-resolution-soundness-and-completeness-cnf-conversion) and [Chapter 9](09-First-Order-Logic.md#95-resolution-theorem-proving-completeness-stated).

## U

**UCB1**
The bandit rule of Auer, Cesa-Bianchi and Fischer (2002) that pulls the arm with the largest upper confidence bound, its average reward plus $c\sqrt{\ln N / n}$. Its regret grows only logarithmically in the number of pulls.
See [Chapter 6](06-Games-and-Adversarial-Search.md#65-monte-carlo-tree-search-and-uct) and [Chapter 15](15-Reinforcement-Learning.md#151-learning-from-rewards-exploration-vs-exploitation-multi-armed-bandits).

**UCT**
Upper Confidence bounds applied to Trees (Kocsis and Szepesvári, 2006): Monte Carlo tree search that uses UCB1 at every node to choose which child to visit. The probability that it chooses a wrong move at the root tends to zero as iterations grow.
See [Chapter 6](06-Games-and-Adversarial-Search.md#65-monte-carlo-tree-search-and-uct).

**Unification**
Finding a substitution that makes two expressions identical, the one primitive operation of first-order inference. Robinson's 1965 algorithm finds a most general unifier (MGU), from which every other unifier follows by further substitution.
See [Chapter 9](09-First-Order-Logic.md#93-unification-robinson-1965-from-scratch).

**Uniform-cost search**
Search that expands the node of lowest path cost $g(n)$ first, using a priority queue. On an explicit graph it is Dijkstra's algorithm; it is complete and cost-optimal when every action cost is at least some $\varepsilon > 0$.
See [Chapter 3](03-Uninformed-Search.md#33-uninformed-search-strategies).

**Uninformed search**
Search that uses no information about how close a state is to the goal, also called blind search: it can only generate successors and recognise a goal. Breadth-first, uniform-cost, depth-first, depth-limited and iterative deepening search are its classic strategies.
See [Chapter 3](03-Uninformed-Search.md#33-uninformed-search-strategies).

## V

**Validity**
A sentence is valid (a tautology) if it is true in every model, satisfiable if it is true in at least one, and unsatisfiable if in none. $\alpha \models \beta$ exactly when $\alpha \wedge \lnot\beta$ is unsatisfiable.
See [Chapter 8](08-Propositional-Logic-and-SAT.md#82-syntax-and-semantics-entailment-truth-tables).

**Value iteration**
Solving an MDP by applying the Bellman update $U \leftarrow BU$ to all states repeatedly, then returning the greedy policy. Because the update is a contraction it converges geometrically to the unique solution.
See [Chapter 14](14-Making-Decisions.md#144-value-iteration-convergence-proved-contraction-policy-iteration).

**Value of perfect information**
The expected gain in utility from learning a variable's value before deciding: the expected best utility with the information minus the best utility without it. It is never negative, is not additive, and does not depend on the order of observations.
See [Chapter 14](14-Making-Decisions.md#142-decision-networks-value-of-information-computed).

**Variable elimination**
Exact inference in Bayesian networks that sums out hidden variables one at a time, multiplying only the factors that mention each. Its cost is exponential in the treewidth set by the elimination order, so it is linear on polytrees.
See [Chapter 12](12-Probabilistic-Reasoning.md#124-exact-inference-enumeration-variable-elimination-from-scratch).

**VCG mechanism**
The Vickrey-Clarke-Groves mechanism: choose the outcome that maximises total reported value, and charge each agent the harm its presence does to the others. Truthful reporting is a dominant strategy, and it generalises the Vickrey auction to many items.
See [Chapter 19](19-Multi-Agent-Systems.md#194-mechanism-design-and-auctions).

**Vickrey auction**
The second-price sealed-bid auction (Vickrey 1961): the highest bid wins and pays the second-highest bid. Bidding one's true value is a dominant strategy, so the auction is strategy-proof.
See [Chapter 19](19-Multi-Agent-Systems.md#194-mechanism-design-and-auctions).

**Viterbi algorithm**
Dynamic programming that finds the most likely state sequence in an HMM by keeping, for each state at each step, the probability of the best path ending there and a back-pointer, in $O(S^2 t)$ time.
See [Chapter 13](13-Reasoning-over-Time.md#133-hidden-markov-models-forward-algorithm-viterbi-from-scratch) and [Chapter 16](16-Natural-Language-Processing.md#163-classic-tasks-classification-tagging-hmm-pos-tagging-parsing-cky-from-scratch).

**Von Neumann-Morgenstern theorem**
The result that if an agent's preferences over lotteries satisfy six axioms (orderability, transitivity, continuity, substitutability, monotonicity, decomposability), there is a utility function whose expected value orders the lotteries exactly as the agent does.
See [Chapter 14](14-Making-Decisions.md#141-utility-theory-expected-utility-von-neumann-morgenstern-axioms-stated).

## W

**WalkSAT**
Local search for SAT: pick a random unsatisfied clause, and with probability $p$ flip a random variable in it, otherwise flip the one that breaks the fewest satisfied clauses. It is incomplete: it cannot prove unsatisfiability.
See [Chapter 8](08-Propositional-Logic-and-SAT.md#85-dpll-from-scratch-walksat).

**Weighted A\***
A\* with an inflated heuristic, $f = g + w\,h$ with $w > 1$. It expands far fewer nodes and its solution costs at most $w$ times the optimum.
See [Chapter 4](04-Heuristic-Search.md#45-weighted-a-and-anytime-search).

**Winograd schema**
A pair of sentences in which changing one word flips what a pronoun refers to, as in "the trophy doesn't fit into the suitcase because it is too large / too small". Resolving it needs everyday knowledge, so Levesque proposed such pairs (2011) as a sharper test than the imitation game.
See [Chapter 1](01-What-Is-AI.md#12-turings-question-and-the-imitation-game), [Chapter 16](16-Natural-Language-Processing.md#161-why-language-is-hard-ambiguity-at-every-level) and [Chapter 21](21-Where-AI-Goes.md#213-common-sense-world-models-embodied-ai).

**Word vector**
A dense vector representing a word, built so that words used in similar contexts get similar vectors, compared by cosine. Counting co-occurrences, reweighting with PPMI and compressing with the SVD gives one kind; word2vec and GloVe learn them.
See [Chapter 16](16-Natural-Language-Processing.md#164-word-vectors-and-meaning) and [Chapter 17](17-Large-Language-Models.md#171-what-a-language-model-is-predicting-the-next-token).

**World model**
A learned model of how the environment responds to actions, predicting the next state and reward, with which an agent can plan in imagination.
See [Chapter 15](15-Reinforcement-Learning.md#156-model-based-rl-and-planning-dyna-alphazeromuzero-schrittwieser-et-al-2020) and [Chapter 21](21-Where-AI-Goes.md#213-common-sense-world-models-embodied-ai).

## Z

**Zero-sum game**
A game in which what one player wins the other loses, so one number per outcome describes both players' interests. Chess scored 1, ½, 0 is constant-sum, which is equivalent.
See [Chapter 6](06-Games-and-Adversarial-Search.md#61-games-as-search-zero-sum-game-trees) and [Chapter 19](19-Multi-Agent-Systems.md#191-games-in-normal-form-dominant-strategies-nash-equilibrium).

**Zipf's law**
The observation that a word's frequency is roughly inversely proportional to its rank: the second most common word occurs about half as often as the first. However much text you collect, most words and word sequences are rare or unseen.
See [Chapter 16](16-Natural-Language-Processing.md#161-why-language-is-hard-ambiguity-at-every-level).
