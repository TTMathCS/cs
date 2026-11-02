import heapq


def select_activities(start, finish):
    """The most activities that do not overlap (one room): always take the one that finishes first.
    Returns their numbers. An activity [s, f) may start exactly when the previous one finishes."""
    order = sorted(range(len(start)), key=lambda i: (finish[i], i))
    chosen, free_at = [], float("-inf")
    for i in order:
        if start[i] >= free_at:              # it starts after the last chosen one ends: take it
            chosen.append(i)
            free_at = finish[i]
    return chosen


def rooms_needed(start, finish):
    """The fewest rooms that hold every activity (interval partitioning)."""
    order = sorted(range(len(start)), key=lambda i: (start[i], i))
    ends = []                                # a min-heap of the times when busy rooms become free
    for i in order:
        if ends and ends[0] <= start[i]:     # the room that frees up first is free in time: reuse it
            heapq.heapreplace(ends, finish[i])
        else:
            heapq.heappush(ends, finish[i])  # otherwise open a new room
    return len(ends)


if __name__ == "__main__":
    s = [1, 3, 0, 5, 3, 5, 6, 7, 8, 2, 12]
    f = [4, 5, 6, 7, 9, 9, 10, 11, 12, 14, 16]
    chosen = select_activities(s, f)
    print(len(chosen), chosen)
    print(rooms_needed(s, f))
