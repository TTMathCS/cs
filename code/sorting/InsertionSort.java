import java.util.Arrays;

public class InsertionSort {
    /** Sorts a in place, smallest first. */
    static void insertionSort(int[] a) {
        for (int i = 1; i < a.length; i++) {
            int key = a[i];                           // a[0..i-1] is sorted; insert a[i] into it
            int j = i - 1;
            while (j >= 0 && a[j] > key) {            // shift bigger values one place right
                a[j + 1] = a[j];
                j--;
            }
            a[j + 1] = key;                           // drop the key into the gap
        }
    }

    public static void main(String[] args) {
        int[][] tests = {{12, 11, 13, 5, 6}, {38, 27, 43, 3, 9, 82, 10}, {}};
        for (int[] a : tests) {
            insertionSort(a);
            System.out.println(Arrays.toString(a));
        }
    }
}
