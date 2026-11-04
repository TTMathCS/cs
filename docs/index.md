---
template: home.html
title: Algorithms
---

# Algorithms, topic by topic

<div class="start-band" markdown>

New here? Start with cards and paper

Six short lessons, about five minutes each. No computer and no coding needed.

1. [**What is an algorithm?** *exact steps, like a recipe*](first-steps/01-What-Is-an-Algorithm.md)
2. [**Sorting cards** *two ways, and which is faster*](first-steps/02-Sorting-Cards.md)
3. [**Guess my number** *1 to 100 in seven guesses*](first-steps/03-Guess-My-Number.md)
4. [**Finding the way** *the shortest path through a maze*](first-steps/04-Finding-the-Way.md)
5. [**Repeat until done** *loops and decisions*](first-steps/05-Repeat-Until-Done.md)
6. [**How a computer learns** *apples or lemons?*](first-steps/06-How-a-Computer-Learns.md)

[Begin lesson 1 →](first-steps/01-What-Is-an-Algorithm.md)

</div>

An algorithm is a recipe a computer can follow: exact steps that turn an input into the answer. This site goes
through the classic ones a topic at a time. Every page says what the algorithm does, how it works in plain words,
gives working code in **Python, Java and C++**, and then opens up, if you want, into a worked example, the math of
why it is correct and how fast it is, and an animation you can step through.

The picture above is one of them at work: nine real places on Mars joined by roads as long as the true distances
between them, and the shortest route from Erebus Montes to Gale crater found by
[Dijkstra's algorithm](graphs/dijkstra.md).

## Find your level

| Level | For whom | Where to go |
|---|---|---|
| **Beginner** | new to computing, young learners, a class | [Start](first-steps/index.md): the six lessons above |
| **Intermediate** | students who can read a little code | the [Algorithms](#algorithms) pages (code in Python, Java and C++), the first chapters of each [Book](#books), and the [Topics](topics/index.md) guides |
| **Expert** | professionals, university and beyond | the later chapters of each Book, the Expert part of each [Topics](topics/index.md) guide, and [What's new](new.md) for the latest research |

Every page shows its level under the title.

## Books { #books }

Want the whole road, not one algorithm at a time? The [Books](books/index.md) are full courses, from the first idea
to research, with every method built from scratch, proved, traced by hand and tested in code.

| Book | What is in it |
| --- | --- |
| [Algorithms](books/algorithms/index.md) | 25 chapters: cost and recursion, sorting, hashing, trees, heaps, design techniques, graphs, strings, number theory, geometry, randomness, NP-completeness, approximation, big data and the open problems |
| [Machine learning](books/machine-learning/index.md) | 23 chapters: data, linear and logistic models, optimization, evaluation, kernels, SVMs, trees and boosting, Bayesian models, clustering, PCA, neural networks from scratch, CNNs, sequence models, transformers, generative models, learning theory and the frontier |
| [Artificial intelligence](books/ai/index.md) | 21 chapters: agents, search, heuristics, games, constraints, logic and SAT, planning, knowledge, Bayesian networks, filtering, decisions, reinforcement learning, language, large language models, robotics, game theory, safety and the frontier |

## Algorithms { #algorithms }

| Topic | What is in it |
| --- | --- |
| [Foundations](foundations/index.md) | How we measure speed (Big-O) and how recursion works: the two ideas every other page uses |
| [Sorting](sorting/index.md) | Eight ways to put a list in order, from bubble sort to radix sort, and when each one wins |
| [Searching](searching/index.md) | Binary search and its cousins: halving the answer, two pointers and the sliding window |
| [Data structures](data-structures/index.md) | Stacks, queues, hash tables, heaps, search trees, union-find, Fenwick and segment trees, tries |
| [Graphs](graphs/index.md) | Breadth- and depth-first search, topological order, shortest paths, spanning trees, strongly connected parts |
| [Dynamic programming](dp/index.md) | Solving a big problem by remembering the answers to its smaller ones: coins, knapsacks, subsequences, edit distance |
| [Greedy](greedy/index.md) | Taking the best-looking step every time, and how to prove that it works: scheduling and Huffman codes |
| [Strings](strings/index.md) | Finding a pattern in a text fast: KMP, Rabin-Karp and the Z-algorithm |
| [Number theory](number-theory/index.md) | Greatest common divisors, primes by the sieve, and powers in $O(\log n)$ steps |
| [Backtracking](backtracking/index.md) | Trying every choice, but giving up early on dead ends: subsets, permutations, N-Queens |

New to this? Start with [How to read this site](start.md), then [Big-O](foundations/big-o.md), then
[sorting](sorting/index.md).
