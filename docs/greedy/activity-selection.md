# Activity selection

*Many activities want one room; each has a start and an end time. Choose as many as possible that do not
overlap. The answer: always take the activity that finishes first.*

| Time | Extra space | Output |
|---|---|---|
| $O(n \log n)$ (sorting), then $O(n)$ | $O(n)$ | the most activities that fit, and which |

## The idea

Natural rules that **fail**:

- *Shortest first:* a short talk in the middle can block two long ones on either side.
- *Earliest start first:* one all-day booking that starts first blocks everything.
- *Fewest conflicts first:* there are counterexamples to this too.

The rule that **works**: pick the activity that **ends earliest**, throw away everything that overlaps it, and
repeat. Ending early leaves the most time for the rest.

Here an activity uses the half-open time $[s, f)$: it may start exactly when another one ends.

The same sorted list also answers a second question: **how many rooms** are needed to hold **all** the
activities? Go through them by start time, and reuse the room that becomes free first if it is free in time;
otherwise open a new room. A [min-heap](../data-structures/binary-heap.md) of end times finds that room.

## How it works

**One room, most activities**

1. Sort the activities by finishing time.
2. Keep `free_at`, the time the room becomes free (at first, minus infinity).
3. For each activity in order: if it starts at or after `free_at`, take it and set `free_at` to its end.

**All activities, fewest rooms**

1. Sort by start time.
2. For each activity: if the earliest end time in the heap is at or before its start, replace that end time with
   this activity's end (same room). Otherwise push its end time (a new room).
3. The size of the heap is the number of rooms.

## Code

=== "Python"

    ```python
    --8<-- "greedy/activity_selection.py"
    ```

=== "Java"

    ```java
    --8<-- "greedy/ActivitySelection.java"
    ```

=== "C++"

    ```cpp
    --8<-- "greedy/activity_selection.cpp"
    ```

Output: `4 [0, 3, 7, 10]`, four activities in one room, and `6`: holding all eleven needs six rooms, because at
time 8 six activities are running at once.

## When to use it

- **Booking one resource:** a room, a telescope, a launch pad, a single machine; the most jobs that fit.
- **Interval scheduling in general:** keeping the most non-overlapping intervals, or (the same thing) removing
  the fewest intervals so the rest do not overlap.
- **Fewest rooms or machines** for a fixed timetable: the interval partitioning version.
- **Fewest points that hit every interval** (for example, fewest arrows to burst balloons): sort by end and put a
  point at each chosen end.

## Common mistakes

- **Sorting by start time** for the one-room question.
- **Open vs closed intervals:** decide whether an activity ending at 5 and one starting at 5 overlap, and use
  `>=` or `>` to match.
- **Weighted activities:** if each activity has a value and you want the most **value**, greedy fails; use dynamic
  programming over the activities sorted by end (weighted interval scheduling).

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: eleven activities"

    Sorted by finishing time (activity number, start, finish):

    | # | start | finish | free from | decision |
    |---|---|---|---|---|
    | 0 | 1 | 4 | −∞ | **take**, busy until 4 |
    | 1 | 3 | 5 | 4 | skip (3 < 4) |
    | 2 | 0 | 6 | 4 | skip |
    | 3 | 5 | 7 | 4 | **take**, busy until 7 |
    | 4 | 3 | 9 | 7 | skip |
    | 5 | 5 | 9 | 7 | skip |
    | 6 | 6 | 10 | 7 | skip |
    | 7 | 7 | 11 | 7 | **take** (starts exactly at 7), busy until 11 |
    | 8 | 8 | 12 | 11 | skip |
    | 9 | 2 | 14 | 11 | skip |
    | 10 | 12 | 16 | 11 | **take** |

    Four activities: 0, 3, 7, 10. This is the example from *Introduction to Algorithms*.

??? abstract "The math: why earliest finish is optimal, and why the room count is right"

    **Greedy stays ahead.** Let the greedy choices be $g_1, g_2, \dots, g_k$ and any other valid choice be
    $o_1, o_2, \dots, o_m$, both in time order. Claim: $f(g_i) \le f(o_i)$ for every $i \le \min(k, m)$.

    - $i = 1$: $g_1$ has the earliest finish of all activities.
    - Step: if $f(g_{i-1}) \le f(o_{i-1}) \le s(o_i)$, then $o_i$ was still available when greedy chose $g_i$,
      and greedy chose the earliest finisher among those available, so $f(g_i) \le f(o_i)$.

    If $m > k$, then $o_{k+1}$ starts after $f(o_k) \ge f(g_k)$ and would still have been available to greedy, which
    would not have stopped. So $k \ge m$: greedy is optimal.

    **Rooms.** Let $d$ be the largest number of activities running at one moment (the *depth*). Any schedule needs
    at least $d$ rooms. The heap method opens a new room only when every open room is busy at that start time,
    which means that many activities are running at once; so it never opens more than $d$. Hence it uses exactly
    $d$ rooms.

    **Time.** Sorting is $O(n \log n)$; the scan is $O(n)$, and each heap operation $O(\log n)$.

??? tip "Watch it step by step"

    Rows are the activities sorted by finishing time; orange is the one being looked at, green are taken, faded are
    skipped.

    <div class="cs-anim" data-anim="activity-selection"></div>

??? info "Variations and related ideas"

    - **Weighted interval scheduling:** sort by end, then
      $\text{best}[i] = \max(\text{best}[i-1],\; v_i + \text{best}[p(i)])$, where $p(i)$ is the last activity
      ending before $i$ starts (found by [binary search](../searching/binary-search.md)); $O(n \log n)$.
    - **Scheduling to minimize lateness:** with deadlines, do jobs in order of deadline (earliest deadline first).
    - **Interval graphs:** intervals as vertices, overlaps as edges. Activity selection is a maximum independent
      set, and room counting is a colouring, both easy here though hard on general graphs.

## See also

- [Greedy algorithms](index.md)
- [Binary heap](../data-structures/binary-heap.md)
- [0/1 knapsack](../dp/knapsack.md): when greedy is not enough

## References

- T. H. Cormen et al., *Introduction to Algorithms*, 4th ed., Section 15.1 (an activity-selection problem).
- J. Kleinberg and É. Tardos, *Algorithm Design*, Section 4.1 (interval scheduling: the greedy algorithm stays ahead).
