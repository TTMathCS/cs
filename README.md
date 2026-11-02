# Algorithms

Computer algorithms topic by topic: https://cs.akadian.ca/ (part of Mars – your new home, www.akadian.ca).
Built with MkDocs Material in the same look as cryptography.akadian.ca and math.akadian.ca; GitHub Pages
publishes it on every push to `main` (`.github/workflows/pages.yml`), so a push here is a publish.

## Layout

```
mkdocs.yml               the site and its menu: one section per topic
docs/index.md            the first page: the list of topics
docs/<topic>/            one folder per topic (foundations, sorting, searching, data-structures, graphs, dp,
                         greedy, strings, number-theory, backtracking); index.md lists its pages
code/<topic>/            every algorithm in Python (name.py), Java (CamelName.java) and C++ (name.cpp)
docs/anim/               the step-by-step animations' frames (made by tools/anim, never edited by hand)
docs/javascripts/anim.js draws the animations; nothing moves until the reader presses Play or Step
docs/stylesheets/        mars.css (the akadian.ca look), cs.css (facts tables, closed boxes, animations)
docs/images/             the banner (drawn by tools/hero) and the background pictures, sources in images/README.md
tools/test_code.py       runs all three languages of every algorithm and checks they print the same lines
tools/anim/              make_frames.py and frames_<topic>.py: run the real algorithm, record each step
```

## Every page has the same parts

Title and a one-line summary in italics; a small facts table (time, space, output); The idea; How it works;
Code (three tabs, pulled from `code/` with `--8<--`, so the page always shows the tested file) and its output;
When to use it; Common mistakes; Going deeper (four closed boxes: a sample walkthrough, the math, "Watch it step
by step" with the animation, variations); See also; References.

## Adding an algorithm

1. Write `code/<topic>/<name>.py`, `<Name>.java` and `<name>.cpp`, each ending with a small demo that prints its
   results. `python3 tools/test_code.py <name>` must say the three agree (needs python3, Java 17+, g++).
2. Add an animation as a function marked `@anim` in `tools/anim/frames_<topic>.py`, then run
   `python3 tools/anim/make_frames.py <anim-name>`.
3. Write `docs/<topic>/<page>.md` with the parts above, add it to `nav:` in `mkdocs.yml` and to the topic's
   `index.md` table.
4. `mkdocs build --strict` must pass before the push.

To try it locally: `pip install "mkdocs-material>=9.6,<9.7"` then `mkdocs serve`.
