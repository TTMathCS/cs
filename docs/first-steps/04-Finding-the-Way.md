# 4. Finding the way

*About 5 minutes · You need: squared paper, a pencil*

## Try it

Draw a maze on squared paper: a grid of about 8 by 8 squares, with some squares shaded as walls. Mark a start **S** and a finish **F**.

Now find the shortest way without guessing:

1. Write **0** in the start square.
2. Write **1** in every open square next to a 0 (up, down, left, right).
3. Write **2** in every empty open square next to a 1. Then 3 next to the 2s, and so on.
4. When you write a number in **F**, stop. Walk back from F, always stepping to a number one smaller. That is a shortest path.

## What's happening

The numbers spread out from the start in **rings**, like a ripple in a pond. A square gets its number the first moment the ripple reaches it, so the number is its true distance from the start. This is **breadth-first search**.

When paths have different lengths, like roads on a map, the same idea with a little more bookkeeping is **Dijkstra's algorithm**. Map apps, video games and the internet's routers all use it.

??? question "What happens if F never gets a number?"
    There is no way through: the walls cut F off from S. The algorithm tells you that too, which is just as useful.

**Next:** [5. Repeat until done](05-Repeat-Until-Done.md) · Going further: [Breadth-first search](../graphs/bfs.md), [Shortest routes guide](../topics/Shortest-routes.md)
