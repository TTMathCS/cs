# How to read this site

## Every page has the same parts

| Part | What it gives you |
| --- | --- |
| **Facts box** | Under the title: how fast it is, how much extra memory it needs, and other properties at a glance |
| **The idea** | The algorithm in plain words, with no code |
| **How it works** | The exact steps, numbered |
| **Code** | Python, Java and C++, in tabs. Pick a language once and every page remembers it |
| **When to use it** | Where it is the right tool, and where something else is better |
| **Common mistakes** | The bugs people really write |
| **Going deeper** | Closed boxes you can open: a worked example, the math, an animation, and related ideas |

## The code

All the code on this site is run before it is published. Each algorithm ends with a small demo, and a test runs the
Python, Java and C++ versions and checks that all three print exactly the same lines (the demo's output is written
under the code). The code favours being clear over being clever: plain loops, comments on the lines that matter,
and no libraries beyond each language's standard one.

- **Python** 3.8 or newer: save as a `.py` file and run `python3 file.py`.
- **Java** 17 or newer: the file name must match the class, for example `BubbleSort.java`; run
  `javac BubbleSort.java` then `java BubbleSort`.
- **C++** 17: `g++ -std=c++17 -O2 file.cpp` then `./a.out`.

## The math

Formulas are typeset as real math. You do not need them to use an algorithm, which is why they sit in the closed
"Going deeper" boxes. The notation used most is:

| Symbol | Read it as |
| --- | --- |
| $n$ | the size of the input (how many values, characters or vertices) |
| $V$, $E$ | the number of vertices and edges in a graph |
| $O(f(n))$ | "grows no faster than $f(n)$", ignoring constant factors ([Big-O](foundations/big-o.md)) |
| $\Theta(f(n))$ | "grows exactly like $f(n)$", up to constant factors |
| $\log n$ | logarithm base 2 unless written otherwise: how many times you can halve $n$ before reaching 1 |
| $\lfloor x \rfloor$ | $x$ rounded down |

## The animations

Each "Watch it step by step" box runs the real algorithm on a small example. Nothing moves until you press
**Play** or **Step**; **Back** goes one step back and **Reset** starts again. The colours mean the same thing
everywhere:

| Colour | Meaning |
| --- | --- |
| orange | being compared or looked at right now |
| red | being swapped or changed |
| blue | waiting: in the queue, on the stack, or inside the current window |
| green | finished: in its final place, or visited for the last time |
| purple | the answer: the path, the match, the chosen items |
