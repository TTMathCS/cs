import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class Knapsack {
    static List<Integer> items = new ArrayList<>();

    /** 0/1 knapsack: the most value that fits in a bag of capacity cap, each item taken at most once.
     *  Returns the best value; the items (by number) that give it are left in items. */
    static int knapsack(int[] weights, int[] values, int cap) {
        int n = weights.length;
        int[][] best = new int[n + 1][cap + 1];       // best[i][c] = the most value using the first i items, capacity c
        for (int i = 1; i <= n; i++) {
            int w = weights[i - 1], v = values[i - 1];
            for (int c = 0; c <= cap; c++) {
                best[i][c] = best[i - 1][c];                          // leave item i-1 out ...
                if (w <= c && best[i - 1][c - w] + v > best[i][c])    // ... or take it, if it fits and is better
                    best[i][c] = best[i - 1][c - w] + v;
            }
        }
        items = new ArrayList<>();
        for (int i = n, c = cap; i > 0; i--)          // walk back: a changed value means item i-1 was taken
            if (best[i][c] != best[i - 1][c]) { items.add(i - 1); c -= weights[i - 1]; }
        Collections.sort(items);
        return best[n][cap];
    }

    /** The same answer with one row: go through capacities from high to low so each item is used once. */
    static int knapsack1d(int[] weights, int[] values, int cap) {
        int[] best = new int[cap + 1];
        for (int k = 0; k < weights.length; k++)
            for (int c = cap; c >= weights[k]; c--)
                best[c] = Math.max(best[c], best[c - weights[k]] + values[k]);
        return best[cap];
    }

    public static void main(String[] args) {
        int b = knapsack(new int[]{1, 3, 4, 5}, new int[]{1, 4, 5, 7}, 7);
        System.out.println(b + " " + items);
        b = knapsack(new int[]{10, 20, 30}, new int[]{60, 100, 120}, 50);
        System.out.println(b + " " + items);
        System.out.println(knapsack1d(new int[]{1, 3, 4, 5}, new int[]{1, 4, 5, 7}, 7) + " "
                + knapsack1d(new int[]{10, 20, 30}, new int[]{60, 100, 120}, 50));
    }
}
