# 3. Guess my number

*About 5 minutes · You need: a partner*

## Try it

Your partner thinks of a number from 1 to 100. You guess; they say only **"higher"**, **"lower"** or **"yes"**. Count your guesses.

Now play again, but always guess **the middle** of the numbers still possible. Start with 50. If they say "higher", the number is 51 to 100, so guess 75. And so on.

How many guesses did the middle trick need?

## What's happening

Every middle guess throws away **half** of the numbers that are left:

100 → 50 → 25 → 13 → 7 → 4 → 2 → 1

So you never need more than **7 guesses** for 1 to 100. For 1 to 1,000 you need 10; for a million, only 20. Each time the list doubles, you need just one more guess.

This is **binary search**. It is how a computer finds a name in a sorted list of millions in an instant, and why sorting things first (lesson 2) is worth the effort.

??? question "Does the middle trick work if the numbers are not in order?"
    No. "Higher" only tells you something because the numbers are in order. In a jumbled list you would have to check them one by one.

**Next:** [4. Finding the way](04-Finding-the-Way.md) · Going further: [Binary search](../searching/binary-search.md), [Sort and search guide](../topics/Sorting-and-searching.md)
