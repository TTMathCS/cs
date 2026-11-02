import java.util.Arrays;

public class BubbleSort {
    /** Sorts a in place, smallest first. */
    static void bubbleSort(int[] a) {
        int n = a.length;
        for (int end = n - 1; end > 0; end--) {       // after each pass, a[end] is in its final place
            boolean swapped = false;
            for (int i = 0; i < end; i++) {
                if (a[i] > a[i + 1]) {                // neighbours in the wrong order: swap them
                    int t = a[i]; a[i] = a[i + 1]; a[i + 1] = t;
                    swapped = true;
                }
            }
            if (!swapped) break;                      // a whole pass with no swap: already sorted
        }
    }

    public static void main(String[] args) {
        int[][] tests = {{5, 1, 4, 2, 8}, {38, 27, 43, 3, 9, 82, 10}, {1, 2, 3}};
        for (int[] a : tests) {
            bubbleSort(a);
            System.out.println(Arrays.toString(a));
        }
    }
}
