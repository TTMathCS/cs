import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class Lis {
    /** O(n^2): best[i] = the length of the longest increasing subsequence that ends at a[i]. */
    static int lisSlow(int[] a) {
        int[] best = new int[a.length];
        int ans = 0;
        for (int i = 0; i < a.length; i++) {
            best[i] = 1;
            for (int j = 0; j < i; j++)
                if (a[j] < a[i] && best[j] + 1 > best[i]) best[i] = best[j] + 1;
            ans = Math.max(ans, best[i]);
        }
        return ans;
    }

    static List<Integer> seq = new ArrayList<>();

    /** O(n log n): tails[k] = the smallest value that can end an increasing subsequence of length k+1.
     *  Returns the length; one longest increasing subsequence is left in seq. */
    static int lisFast(int[] a) {
        int[] tails = new int[a.length], tailAt = new int[a.length], prev = new int[a.length];
        int len = 0;
        for (int i = 0; i < a.length; i++) {
            int lo = 0, hi = len;                     // the first tail >= a[i] (binary search)
            while (lo < hi) { int mid = (lo + hi) / 2; if (tails[mid] < a[i]) lo = mid + 1; else hi = mid; }
            tails[lo] = a[i]; tailAt[lo] = i;         // extend the longest, or a smaller ending for length lo+1
            if (lo == len) len++;
            prev[i] = lo > 0 ? tailAt[lo - 1] : -1;
        }
        seq = new ArrayList<>();
        for (int i = len > 0 ? tailAt[len - 1] : -1; i != -1; i = prev[i]) seq.add(a[i]);
        Collections.reverse(seq);
        return len;
    }

    public static void main(String[] args) {
        int[][] tests = {{10, 9, 2, 5, 3, 7, 101, 18}, {0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15}};
        for (int[] a : tests) {
            int k = lisFast(a);
            System.out.println(lisSlow(a) + " " + k + " " + seq);
        }
    }
}
