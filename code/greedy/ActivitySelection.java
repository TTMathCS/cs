import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.PriorityQueue;

public class ActivitySelection {
    /** The most activities that do not overlap (one room): always take the one that finishes first.
     *  Returns their numbers. An activity [s, f) may start exactly when the previous one finishes. */
    static List<Integer> selectActivities(int[] start, int[] finish) {
        Integer[] order = new Integer[start.length];
        for (int i = 0; i < order.length; i++) order[i] = i;
        Arrays.sort(order, (x, y) -> finish[x] != finish[y] ? Integer.compare(finish[x], finish[y]) : Integer.compare(x, y));
        List<Integer> chosen = new ArrayList<>();
        long freeAt = Long.MIN_VALUE;
        for (int i : order)
            if (start[i] >= freeAt) {                 // it starts after the last chosen one ends: take it
                chosen.add(i);
                freeAt = finish[i];
            }
        return chosen;
    }

    /** The fewest rooms that hold every activity (interval partitioning). */
    static int roomsNeeded(int[] start, int[] finish) {
        Integer[] order = new Integer[start.length];
        for (int i = 0; i < order.length; i++) order[i] = i;
        Arrays.sort(order, (x, y) -> start[x] != start[y] ? Integer.compare(start[x], start[y]) : Integer.compare(x, y));
        PriorityQueue<Integer> ends = new PriorityQueue<>();   // when busy rooms become free
        for (int i : order) {
            if (!ends.isEmpty() && ends.peek() <= start[i]) ends.poll();   // reuse the room that frees up first
            ends.add(finish[i]);                      // (otherwise this opens a new room)
        }
        return ends.size();
    }

    public static void main(String[] args) {
        int[] s = {1, 3, 0, 5, 3, 5, 6, 7, 8, 2, 12};
        int[] f = {4, 5, 6, 7, 9, 9, 10, 11, 12, 14, 16};
        List<Integer> chosen = selectActivities(s, f);
        System.out.println(chosen.size() + " " + chosen);
        System.out.println(roomsNeeded(s, f));
    }
}
