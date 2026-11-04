# 6. How a computer learns

*About 5 minutes · You need: paper, a pencil*

## Try it

You are a computer that has never seen fruit. You are given examples, each with two measurements:

| Fruit | Weight (grams) | Yellowness (0 to 10) |
|---|---|---|
| apple | 180 | 2 |
| apple | 160 | 3 |
| apple | 200 | 1 |
| lemon | 100 | 9 |
| lemon | 120 | 8 |
| lemon | 90 | 10 |

Draw a graph: weight along the bottom, yellowness up the side. Put a dot for each fruit and label it.

Now a new fruit arrives: **110 grams, yellowness 7**. Find the dot closest to it. What do you guess the new fruit is?

??? question "Answer"
    The closest examples are lemons (120 g, 8 and 100 g, 9), so you guess **lemon**.

## What's happening

You just ran **nearest neighbour**, one of the simplest ways a computer learns. Nobody wrote a rule like "lemons are yellow"; the rule came from the **examples**. With more examples and more measurements, the same idea can sort photos, spot spam or suggest a song.

This is **machine learning**: instead of writing the steps, we give the computer examples and let it find the pattern. Its guesses are only as good as its examples. Show it only green apples, and it may call a red one a tomato.

??? question "A new fruit weighs 140 grams with yellowness 5. What now?"
    It is about halfway between the groups, so the guess is unsure. Real systems say how confident they are, and more examples or more measurements (shape, smell) help.

**You finished the start!** Next: the [Topics](../topics/index.md), or the [Machine learning book](../books/machine-learning/index.md) from chapter 1.
