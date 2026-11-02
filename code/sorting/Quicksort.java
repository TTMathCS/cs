import java.util.Arrays;
import java.util.Random;

public class Quicksort {
    static final Random RNG = new Random();

    /** Sorts a[lo..hi] in place (both ends included), smallest first. */
    static void quicksort(int[] a, int lo, int hi) {
        if (lo >= hi) return;
        int p = partition(a, lo, hi);                 // a[p] is now in its final place
        quicksort(a, lo, p - 1);                      // sort what is smaller ...
        quicksort(a, p + 1, hi);                      // ... and what is larger
    }

    /** Lomuto partition: uses a[hi] as the pivot, returns where the pivot ends up. */
    static int partition(int[] a, int lo, int hi) {
        int pivot = a[hi];
        int i = lo;                                   // a[lo..i-1] holds values < pivot
        for (int j = lo; j < hi; j++) {
            if (a[j] < pivot) { swap(a, i, j); i++; }
        }
        swap(a, i, hi);                               // pivot goes between the two parts
        return i;
    }

    /** The safe version: a random pivot makes the slow O(n^2) case vanishingly unlikely. */
    static void quicksortRandom(int[] a, int lo, int hi) {
        if (lo >= hi) return;
        swap(a, lo + RNG.nextInt(hi - lo + 1), hi);   // move a random value into the pivot slot
        int p = partition(a, lo, hi);
        quicksortRandom(a, lo, p - 1);
        quicksortRandom(a, p + 1, hi);
    }

    static void swap(int[] a, int i, int j) { int t = a[i]; a[i] = a[j]; a[j] = t; }

    public static void main(String[] args) {
        int[] a = {10, 80, 30, 90, 40, 50, 70};
        quicksort(a, 0, a.length - 1);
        System.out.println(Arrays.toString(a));
        int[] b = {38, 27, 43, 3, 9, 82, 10};
        quicksort(b, 0, b.length - 1);
        System.out.println(Arrays.toString(b));
        int[] c = {5, 1, 4, 2, 8, 5, 5};
        quicksortRandom(c, 0, c.length - 1);
        System.out.println(Arrays.toString(c));
    }
}
