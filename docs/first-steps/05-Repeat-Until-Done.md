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

**Next:** [6. How a computer learns](06-How-a-Computer-Learns.md) · Going further: [Recursion](../foundations/recursion.md), [How to read this site](../start.md)
