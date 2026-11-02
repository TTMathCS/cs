import java.util.Arrays;

public class Heapsort {
    /** Sorts a in place, smallest first, using a max-heap stored in a itself. */
    static void heapsort(int[] a) {
        int n = a.length;
        for (int i = n / 2 - 1; i >= 0; i--)          // build the heap: sift down every parent, last first
            siftDown(a, i, n);
        for (int end = n - 1; end > 0; end--) {
            int t = a[0]; a[0] = a[end]; a[end] = t;  // the largest goes to the back ...
            siftDown(a, 0, end);                      // ... and the heap shrinks by one
        }
    }

    /** Moves a[i] down until both children are smaller (only a[0..n-1] is the heap). */
    static void siftDown(int[] a, int i, int n) {
        while (true) {
            int big = i, left = 2 * i + 1, right = 2 * i + 2;
            if (left < n && a[left] > a[big]) big = left;
            if (right < n && a[right] > a[big]) big = right;
            if (big == i) return;
            int t = a[i]; a[i] = a[big]; a[big] = t;
            i = big;
        }
    }

    public static void main(String[] args) {
        int[][] tests = {{4, 10, 3, 5, 1}, {38, 27, 43, 3, 9, 82, 10}, {7, 7, 1}};
        for (int[] a : tests) {
            heapsort(a);
            System.out.println(Arrays.toString(a));
        }
    }
}
