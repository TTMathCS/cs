# 5. Repeat until done

*About 5 minutes · You need: a partner, a few small objects*

## Try it

Your partner is a robot. It understands only these commands:

- `step` (one step forward), `turn left`, `turn right`, `pick up`
- `repeat N times: ...`
- `if there is something in front: ... otherwise: ...`

Put an object 4 steps in front of the robot. Write a program to fetch it. Then write a shorter one using `repeat`.

Now put the object somewhere the robot can't see, straight ahead. Write a program that works **however far** it is.

??? question "One answer"
    ```
    repeat until there is something in front:
        step
    pick up
    ```

## What's happening

Every program in the world is built from a few ideas:

- **Steps in order** (a sequence).
- **Loops**: repeat steps, a set number of times or until something is true.
- **Decisions**: `if ... otherwise ...`.

With just these, people have written games, phone apps and the software that flew a helicopter on Mars. Python, Java and C++ all have them; they only spell them differently (`for`, `while`, `if`).

??? question "What goes wrong if you write "repeat until there is something in front: turn left"?"
    If nothing is in front, the robot spins forever. A loop must change something that will eventually make it stop. Programmers call a never-ending loop an **infinite loop**.

<figure class="sketch"><span class="ai-tag">AI-created</span><svg viewBox="0 0 640 380" role="img" aria-labelledby="sk-cs-loop-t"><title id="sk-cs-loop-t">A robot steps forward until there is something in front of it and then picks it up, a loop that works however far away the object is</title><defs><filter id="sk-cs-loop-pen"><feTurbulence type="fractalNoise" baseFrequency="0.03" numOctaves="2" seed="3"/><feDisplacementMap in="SourceGraphic" scale="3.2"/></filter><filter id="sk-cs-loop-paper"><feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="3" seed="7"/><feColorMatrix values="0 0 0 0 0.45  0 0 0 0 0.35  0 0 0 0 0.25  0 0 0 .10 0"/></filter><pattern id="sk-cs-loop-hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(35)"><line x1="0" y1="0" x2="0" y2="7" stroke="#8a4a2a" stroke-width="1.1" opacity=".55"/></pattern><pattern id="sk-cs-loop-dots" width="9" height="9" patternUnits="userSpaceOnUse"><circle cx="2" cy="3" r="1" fill="#8a4a2a" opacity=".5"/><circle cx="6.5" cy="7" r=".8" fill="#8a4a2a" opacity=".4"/></pattern><marker id="sk-cs-loop-ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M1 1L9 5L1 9" fill="none" stroke="#3a2a1e" stroke-width="1.6" stroke-linecap="round"/></marker></defs><rect width="640" height="380" filter="url(#sk-cs-loop-paper)"/><g filter="url(#sk-cs-loop-pen)"><text x="30" y="44" class="h">Repeat until done</text><path class="p" d="M40 210 L600 210"/><path class="p room" d="M52 205 L88 205 L88 175 L70 160 L52 175Z"/><circle cx="160" cy="205" r="3" fill="#3a2a1e" opacity=".5"/><circle cx="250" cy="205" r="3" fill="#3a2a1e" opacity=".5"/><circle cx="340" cy="205" r="3" fill="#3a2a1e" opacity=".5"/><path class="p gold" d="M412 205 L448 205 L448 175 L430 160 L412 175Z"/><path class="p rust" d="M520 205 L548 205 L548 180 L520 180Z"/><text x="534" y="236" text-anchor="middle" class="s">the object</text><path class="p dash" d="M95 185 L470 185" marker-end="url(#sk-cs-loop-ah)"/><text x="70" y="236" text-anchor="middle" class="s">robot</text><path class="p room" d="M60 270 L360 270 L360 372 L60 372Z"/><text x="74" y="298" class="s">repeat until there is</text><text x="74" y="318" class="s">something in front:</text><text x="104" y="338" class="s">step</text><text x="74" y="356" class="s">pick up</text><text x="390" y="300" class="s">Works however far it is.</text><text x="390" y="330" class="s">Steps, loops and decisions:</text><text x="390" y="350" class="s">every program is built from them.</text></g></svg><figcaption>Sketched for this page.</figcaption></figure>

**Next:** [6. How a computer learns](06-How-a-Computer-Learns.md) · Going further: [Recursion](../foundations/recursion.md), [How to read this site](../start.md)
