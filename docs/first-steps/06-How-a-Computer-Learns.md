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

<figure class="play" data-play="fruit"><span class="ai-tag">AI-created</span><figcaption><b>Try it.</b> The six fruits from the table. Tap anywhere to place a new fruit: the guess is the closest example.</figcaption></figure>

## What's happening

You just ran **nearest neighbour**, one of the simplest ways a computer learns. Nobody wrote a rule like "lemons are yellow"; the rule came from the **examples**. With more examples and more measurements, the same idea can sort photos, spot spam or suggest a song.

This is **machine learning**: instead of writing the steps, we give the computer examples and let it find the pattern. Its guesses are only as good as its examples. Show it only green apples, and it may call a red one a tomato.

??? question "A new fruit weighs 140 grams with yellowness 5. What now?"
    It is about halfway between the groups, so the guess is unsure. Real systems say how confident they are, and more examples or more measurements (shape, smell) help.

<figure class="sketch"><span class="ai-tag">AI-created</span><svg viewBox="0 0 640 400" role="img" aria-labelledby="sk-cs-fruit-t"><title id="sk-cs-fruit-t">Apples plotted heavy and not yellow, lemons light and yellow; a new fruit of 110 g and yellowness 7 sits nearest a lemon, so the guess is lemon</title><defs><filter id="sk-cs-fruit-pen"><feTurbulence type="fractalNoise" baseFrequency="0.03" numOctaves="2" seed="3"/><feDisplacementMap in="SourceGraphic" scale="3.2"/></filter><filter id="sk-cs-fruit-paper"><feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="3" seed="7"/><feColorMatrix values="0 0 0 0 0.45  0 0 0 0 0.35  0 0 0 0 0.25  0 0 0 .10 0"/></filter><pattern id="sk-cs-fruit-hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(35)"><line x1="0" y1="0" x2="0" y2="7" stroke="#8a4a2a" stroke-width="1.1" opacity=".55"/></pattern><pattern id="sk-cs-fruit-dots" width="9" height="9" patternUnits="userSpaceOnUse"><circle cx="2" cy="3" r="1" fill="#8a4a2a" opacity=".5"/><circle cx="6.5" cy="7" r=".8" fill="#8a4a2a" opacity=".4"/></pattern><marker id="sk-cs-fruit-ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M1 1L9 5L1 9" fill="none" stroke="#3a2a1e" stroke-width="1.6" stroke-linecap="round"/></marker></defs><rect width="640" height="400" filter="url(#sk-cs-fruit-paper)"/><g filter="url(#sk-cs-fruit-pen)"><text x="30" y="44" class="h">Which dot is nearest?</text><path class="p" d="M80.0 330 L584.0 330 M80.0 330 L80.0 65.0"/><text x="152.0" y="352" text-anchor="middle" class="s">100 g</text><text x="332.0" y="352" text-anchor="middle" class="s">150 g</text><text x="512.0" y="352" text-anchor="middle" class="s">200 g</text><text x="332.0" y="374" text-anchor="middle" class="s">weight</text><text x="70.0" y="85" text-anchor="end" class="s">10</text><text x="70.0" y="210" text-anchor="end" class="s">yellow</text><circle cx="440.0" cy="280" r="8" class="p rust"/><circle cx="368.0" cy="255" r="8" class="p rust"/><circle cx="512.0" cy="305" r="8" class="p rust"/><circle cx="152.0" cy="105" r="8" class="p gold"/><circle cx="224.0" cy="130" r="8" class="p gold"/><circle cx="116.0" cy="80" r="8" class="p gold"/><text x="458.0" y="245.0" class="l">apples</text><text x="267.20000000000005" y="90.0" class="l">lemons</text><path class="p red" d="M181.0 148 L195.0 162 M195.0 148 L181.0 162"/><path class="p dash" d="M188.0 155 L224.0 130"/><text x="195.2" y="175.0" class="s">new: 110 g, 7 → lemon</text></g></svg><figcaption>Sketched for this page from the table above. To scale.</figcaption></figure>

**You finished the start!** Next: the [Topics](../topics/index.md), or the [Machine learning book](../books/machine-learning/index.md) from chapter 1.
