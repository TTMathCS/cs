# 1. What is an algorithm?

*About 5 minutes · You need: a partner, paper*

## Try it

Write instructions for your partner to draw a house: a square with a triangle on top. Your partner must follow **exactly** what you wrote, nothing more, and may not guess what you meant.

Swap and try again. Did your house come out right the first time?

<figure class="play" data-play="strict"><span class="ai-tag">AI-created</span><figcaption><b>Watch it.</b> A strict partner follows the words exactly. Compare the vague steps with the exact ones.</figcaption></figure>

## What's happening

An **algorithm** is a list of steps that solves a problem: a recipe, the rules of a game, directions to school. Computers follow algorithms, but they are like the strict partner: they do exactly what the steps say, even when it is silly.

A good algorithm:

- is **exact**: every step has one meaning ("draw a line 5 cm long", not "draw a line").
- **finishes**: it doesn't go on forever.
- **works every time**, not just for the example you tried.

The word comes from **al-Khwarizmi**, a scholar in Baghdad about 1,200 years ago, who wrote down step-by-step methods for doing arithmetic.

??? question "Is "stir until it looks done" a good step for a computer?"
    No. "Looks done" means different things to different people. A computer needs something it can check, like "stir for 2 minutes" or "stir until the temperature reaches 70 degrees".

<figure class="sketch"><span class="ai-tag">AI-created</span><svg viewBox="0 0 640 400" role="img" aria-labelledby="sk-cs-house-t"><title id="sk-cs-house-t">The instruction "draw a house" can come out as anything, while exact steps, a square with sides of 5 cm and a triangle on top, come out the same every time</title><defs><filter id="sk-cs-house-pen"><feTurbulence type="fractalNoise" baseFrequency="0.03" numOctaves="2" seed="3"/><feDisplacementMap in="SourceGraphic" scale="3.2"/></filter><filter id="sk-cs-house-paper"><feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="3" seed="7"/><feColorMatrix values="0 0 0 0 0.45  0 0 0 0 0.35  0 0 0 0 0.25  0 0 0 .10 0"/></filter><pattern id="sk-cs-house-hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(35)"><line x1="0" y1="0" x2="0" y2="7" stroke="#8a4a2a" stroke-width="1.1" opacity=".55"/></pattern><pattern id="sk-cs-house-dots" width="9" height="9" patternUnits="userSpaceOnUse"><circle cx="2" cy="3" r="1" fill="#8a4a2a" opacity=".5"/><circle cx="6.5" cy="7" r=".8" fill="#8a4a2a" opacity=".4"/></pattern><marker id="sk-cs-house-ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M1 1L9 5L1 9" fill="none" stroke="#3a2a1e" stroke-width="1.6" stroke-linecap="round"/></marker></defs><rect width="640" height="400" filter="url(#sk-cs-house-paper)"/><g filter="url(#sk-cs-house-pen)"><text x="30" y="44" class="h">Exact, or a guess?</text><text x="40" y="90" class="l">"draw a house"</text><path class="p" d="M60 170 L120 130 L180 180 L170 260 L70 250Z"/><text x="60" y="290" class="s">anything could happen</text><text x="340" y="90" class="l">exact steps</text><text x="340" y="120" class="s">1. a square, sides 5 cm</text><text x="340" y="140" class="s">2. a triangle, sides 5 cm,</text><text x="340" y="160" class="s">    on top of the square</text><text x="340" y="180" class="s">3. stop</text><path class="p room" d="M440 310 L540 310 L540 250 L440 250Z"/><path class="p rust" d="M440 250 L490 164 L540 250Z"/><text x="30" y="350" class="s">A good algorithm is exact, it finishes, and it works every time.</text><text x="30" y="374" class="s">The word comes from al-Khwarizmi, Baghdad, about 1,200 years ago.</text></g></svg><figcaption>Sketched for this page.</figcaption></figure>

**Next:** [2. Sorting cards](02-Sorting-Cards.md) · Going further: [Algorithms book, chapter 1](../books/algorithms/01-What-Is-an-Algorithm.md)
