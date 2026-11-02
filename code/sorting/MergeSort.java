import java.util.Arrays;

public class MergeSort {
    /** Sorts a[lo..hi) in place, using tmp as scratch space. */
    static void mergeSort(int[] a, int[] tmp, int lo, int hi) {
        if (hi - lo <= 1) return;                     // 0 or 1 items: already sorted
        int mid = (lo + hi) / 2;
        mergeSort(a, tmp, lo, mid);                   // sort each half ...
        mergeSort(a, tmp, mid, hi);
        merge(a, tmp, lo, mid, hi);                   // ... and merge the two sorted halves
    }

    static void merge(int[] a, int[] tmp, int lo, int mid, int hi) {
        int i = lo, j = mid, k = lo;
        while (i < mid && j < hi)
            tmp[k++] = (a[i] <= a[j]) ? a[i++] : a[j++];   // <= keeps equal values in order (stable)
        while (i < mid) tmp[k++] = a[i++];            // one side is used up; copy the rest
        while (j < hi) tmp[k++] = a[j++];
        System.arraycopy(tmp, lo, a, lo, hi - lo);
    }

    static void mergeSort(int[] a) { mergeSort(a, new int[a.length], 0, a.length); }

    public static void main(String[] args) {
        int[][] tests = {{38, 27, 43, 3, 9, 82, 10}, {5, 1, 4, 2, 8, 5}, {1}};
        for (int[] a : tests) {
            mergeSort(a);
            System.out.println(Arrays.toString(a));
        }
    }
}
