import java.util.Arrays;

public class RadixSort {
    /** Returns a sorted copy of non-negative whole numbers (LSD radix sort, base 10). */
    static int[] radixSort(int[] a) {
        int[] out = a.clone();
        int biggest = 0;
        for (int x : out) biggest = Math.max(biggest, x);
        for (long place = 1; biggest / place > 0; place *= 10)   // one pass per digit, ones first
            out = sortByDigit(out, (int) place);
        return out;
    }

    /** A stable counting sort on one decimal digit. */
    static int[] sortByDigit(int[] a, int place) {
        int[] count = new int[10];
        for (int x : a) count[(x / place) % 10]++;
        for (int d = 1; d < 10; d++) count[d] += count[d - 1];
        int[] out = new int[a.length];
        for (int i = a.length - 1; i >= 0; i--)       // from the back keeps it stable, which radix sort needs
            out[--count[(a[i] / place) % 10]] = a[i];
        return out;
    }

    public static void main(String[] args) {
        System.out.println(Arrays.toString(radixSort(new int[]{170, 45, 75, 90, 802, 24, 2, 66})));
        System.out.println(Arrays.toString(radixSort(new int[]{329, 457, 657, 839, 436, 720, 355})));
        System.out.println(Arrays.toString(radixSort(new int[]{5, 0, 5})));
    }
}
