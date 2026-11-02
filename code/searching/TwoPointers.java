import java.util.Arrays;

public class TwoPointers {
    /** In the sorted array a, finds positions i < j with a[i] + a[j] == target, or null. */
    static int[] pairWithSum(int[] a, int target) {
        int i = 0, j = a.length - 1;
        while (i < j) {
            int s = a[i] + a[j];
            if (s == target) return new int[]{i, j};
            if (s < target) i++;                      // need a bigger sum: move the left pointer right
            else j--;                                 // need a smaller sum: move the right pointer left
        }
        return null;
    }

    /** Moves the distinct values of the sorted array a to its front; returns how many there are. */
    static int removeDuplicates(int[] a) {
        if (a.length == 0) return 0;
        int write = 1;                                // a[0..write-1] holds the distinct values so far
        for (int read = 1; read < a.length; read++)
            if (a[read] != a[write - 1]) a[write++] = a[read];
        return write;
    }

    /** Two walls of heights h[i], h[j] hold (j - i) * min(h[i], h[j]) water; returns the most. */
    static int maxWater(int[] h) {
        int i = 0, j = h.length - 1, best = 0;
        while (i < j) {
            best = Math.max(best, (j - i) * Math.min(h[i], h[j]));
            if (h[i] < h[j]) i++;                     // the shorter wall limits us: only moving it can help
            else j--;
        }
        return best;
    }

    static String pair(int[] p) { return p == null ? "None" : "(" + p[0] + ", " + p[1] + ")"; }

    public static void main(String[] args) {
        System.out.println(pair(pairWithSum(new int[]{1, 2, 4, 7, 11, 15}, 15)));
        System.out.println(pair(pairWithSum(new int[]{1, 2, 4, 7, 11, 15}, 10)));
        int[] a = {1, 1, 2, 3, 3, 3, 4};
        int n = removeDuplicates(a);
        System.out.println(n + " " + Arrays.toString(Arrays.copyOf(a, n)));
        System.out.println(maxWater(new int[]{1, 8, 6, 2, 5, 4, 8, 3, 7}));
    }
}
