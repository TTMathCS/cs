# 2. Sorting cards

*About 5 minutes · You need: 8 playing cards (or 8 papers with numbers), a partner*

## Try it

Shuffle 8 cards and lay them face up in a row. Put them in order, smallest to largest, using one of these methods. Your partner counts every time you **compare** two cards.

**Method A, pick the smallest:** look along the row for the smallest card and move it to the front. Then find the smallest of the rest, and so on.

**Method B, slide into place:** pick up cards one at a time; slide each new card into the right place among the cards already in your hand.

Shuffle and try the other method. Which needed fewer comparisons? Try Method B on cards that are **already almost in order**.

## What's happening

Method A is **selection sort** and Method B is **insertion sort**. With 8 cards, selection sort always makes 28 comparisons. Insertion sort makes up to 28 too, but on cards that are almost in order it needs only about 7.

With a million cards, both would need about 500 thousand million comparisons. Cleverer methods, like **merge sort**, split the pile in half, sort each half, and merge them: about 20 million comparisons for a million cards. That difference is why computer scientists care so much about the method.

??? question "Why does selection sort make 28 comparisons for 8 cards?"
    To find the smallest of 8 it compares 7 times, then 6 for the smallest of the remaining 7, then 5... 7 + 6 + 5 + 4 + 3 + 2 + 1 = 28.

**Next:** [3. Guess my number](03-Guess-My-Number.md) · Going further: [Selection sort](../sorting/selection-sort.md), [Insertion sort](../sorting/insertion-sort.md), [Merge sort](../sorting/merge-sort.md)
