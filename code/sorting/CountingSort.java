import java.util.Arrays;

public class CountingSort {
    /** Returns a sorted copy of a, whose values are whole numbers from 0 to k. Stable. */
    static int[] countingSort(int[] a, int k) {
        int[] count = new int[k + 1];
        for (int x : a) count[x]++;                   // 1. count each value
        for (int v = 1; v <= k; v++)                  // 2. running totals: count[v] = how many are <= v
            count[v] += count[v - 1];
        int[] out = new int[a.length];
        for (int i = a.length - 1; i >= 0; i--)       // 3. place from the back, so equal values keep order
            out[--count[a[i]]] = a[i];
        return out;
    }

    public static void main(String[] args) {
        System.out.println(Arrays.toString(countingSort(new int[]{2, 5, 3, 0, 2, 3, 0, 3}, 5)));
        System.out.println(Arrays.toString(countingSort(new int[]{4, 1, 3, 4, 3}, 4)));
        System.out.println(Arrays.toString(countingSort(new int[]{0}, 0)));
    }
}
