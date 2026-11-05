# 3. Guess my number

*About 5 minutes · You need: a partner*

## Try it

Your partner thinks of a number from 1 to 100. You guess; they say only **"higher"**, **"lower"** or **"yes"**. Count your guesses.

Now play again, but always guess **the middle** of the numbers still possible. Start with 50. If they say "higher", the number is 51 to 100, so guess 75. And so on.

How many guesses did the middle trick need?

<figure class="play" data-play="guessnum"><span class="ai-tag">AI-created</span><figcaption><b>Play it.</b> The computer has picked a number from 1 to 100. Guess with the slider, or press Middle trick and count how few guesses it needs.</figcaption></figure>

## What's happening

Every middle guess throws away **half** of the numbers that are left:

100 → 50 → 25 → 13 → 7 → 4 → 2 → 1

So you never need more than **7 guesses** for 1 to 100. For 1 to 1,000 you need 10; for a million, only 20. Each time the list doubles, you need just one more guess.

This is **binary search**. It is how a computer finds a name in a sorted list of millions in an instant, and why sorting things first (lesson 2) is worth the effort.

??? question "Does the middle trick work if the numbers are not in order?"
    No. "Higher" only tells you something because the numbers are in order. In a jumbled list you would have to check them one by one.

<figure class="sketch"><span class="ai-tag">AI-created</span><svg viewBox="0 0 640 400" role="img" aria-labelledby="sk-cs-halves-t"><title id="sk-cs-halves-t">Numbers left after each middle guess: 100, 50, 25, 13, 7, 4, 2, 1, so 7 guesses are always enough for 1 to 100</title><defs><filter id="sk-cs-halves-pen"><feTurbulence type="fractalNoise" baseFrequency="0.03" numOctaves="2" seed="3"/><feDisplacementMap in="SourceGraphic" scale="3.2"/></filter><filter id="sk-cs-halves-paper"><feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="3" seed="7"/><feColorMatrix values="0 0 0 0 0.45  0 0 0 0 0.35  0 0 0 0 0.25  0 0 0 .10 0"/></filter><pattern id="sk-cs-halves-hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(35)"><line x1="0" y1="0" x2="0" y2="7" stroke="#8a4a2a" stroke-width="1.1" opacity=".55"/></pattern><pattern id="sk-cs-halves-dots" width="9" height="9" patternUnits="userSpaceOnUse"><circle cx="2" cy="3" r="1" fill="#8a4a2a" opacity=".5"/><circle cx="6.5" cy="7" r=".8" fill="#8a4a2a" opacity=".4"/></pattern><marker id="sk-cs-halves-ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M1 1L9 5L1 9" fill="none" stroke="#3a2a1e" stroke-width="1.6" stroke-linecap="round"/></marker></defs><rect width="640" height="400" filter="url(#sk-cs-halves-paper)"/><g filter="url(#sk-cs-halves-pen)"><text x="30" y="44" class="h">Each middle guess throws away half</text><path class="p gold" d="M40 80 L580.0 80 L580.0 102 L40 102Z"/><text x="572.0" y="97" text-anchor="end" class="l">100</text><path class="p gold" d="M40 116 L310.0 116 L310.0 138 L40 138Z"/><text x="326.0" y="133" text-anchor="start" class="l">50</text><text x="600" y="133" text-anchor="end" class="s">guess 1</text><path class="p gold" d="M40 152 L175.0 152 L175.0 174 L40 174Z"/><text x="191.0" y="169" text-anchor="start" class="l">25</text><text x="600" y="169" text-anchor="end" class="s">guess 2</text><path class="p gold" d="M40 188 L110.2 188 L110.2 210 L40 210Z"/><text x="126.2" y="205" text-anchor="start" class="l">13</text><text x="600" y="205" text-anchor="end" class="s">guess 3</text><path class="p gold" d="M40 224 L77.80000000000001 224 L77.80000000000001 246 L40 246Z"/><text x="93.80000000000001" y="241" text-anchor="start" class="l">7</text><text x="600" y="241" text-anchor="end" class="s">guess 4</text><path class="p gold" d="M40 260 L61.6 260 L61.6 282 L40 282Z"/><text x="77.6" y="277" text-anchor="start" class="l">4</text><text x="600" y="277" text-anchor="end" class="s">guess 5</text><path class="p gold" d="M40 296 L50.8 296 L50.8 318 L40 318Z"/><text x="66.8" y="313" text-anchor="start" class="l">2</text><text x="600" y="313" text-anchor="end" class="s">guess 6</text><path class="p rust" d="M40 332 L45.4 332 L45.4 354 L40 354Z"/><text x="61.4" y="349" text-anchor="start" class="l">1</text><text x="600" y="349" text-anchor="end" class="s">guess 7</text><text x="30" y="384" class="s">Never more than 7 guesses for 1 to 100; 10 for a thousand; 20 for a million.</text></g></svg><figcaption>Sketched for this page. Bar lengths to scale.</figcaption></figure>

**Next:** [4. Finding the way](04-Finding-the-Way.md) · Going further: [Binary search](../searching/binary-search.md), [Sort and search guide](../topics/Sorting-and-searching.md)
