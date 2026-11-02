import java.util.Arrays;

public class SelectionSort {
    /** Sorts a in place, smallest first. */
    static void selectionSort(int[] a) {
        int n = a.length;
        for (int i = 0; i < n - 1; i++) {
            int smallest = i;                         // find the smallest value in a[i..n-1]
            for (int j = i + 1; j < n; j++)
                if (a[j] < a[smallest]) smallest = j;
            int t = a[i]; a[i] = a[smallest]; a[smallest] = t;   // put it at position i
        }
    }

    public static void main(String[] args) {
        int[][] tests = {{64, 25, 12, 22, 11}, {38, 27, 43, 3, 9, 82, 10}, {2, 1}};
        for (int[] a : tests) {
            selectionSort(a);
            System.out.println(Arrays.toString(a));
        }
    }
}
