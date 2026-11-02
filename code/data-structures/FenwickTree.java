import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class FenwickTree {
    final int n;
    final long[] t;                                   // t[i] holds the sum of the last lowbit(i) values up to i

    /** Prefix sums with updates, both in O(log n). Positions are 1..n inside the tree. */
    FenwickTree(int n) { this.n = n; t = new long[n + 1]; }

    /** a[i] += delta, for i in 0..n-1. */
    void add(int i, long delta) {
        for (i++; i <= n; i += i & -i) t[i] += delta; // jump to the next range that covers position i
    }

    /** a[0] + ... + a[i-1]. */
    long prefix(int i) {
        long s = 0;
        for (; i > 0; i -= i & -i) s += t[i];         // drop the lowest set bit: the ranges tile [1, i]
        return s;
    }

    /** a[lo] + ... + a[hi - 1]. */
    long rangeSum(int lo, int hi) { return prefix(hi) - prefix(lo); }

    public static void main(String[] args) {
        int[] a = {5, 2, 9, -3, 5, 20, 10, -7};
        FenwickTree f = new FenwickTree(a.length);
        for (int i = 0; i < a.length; i++) f.add(i, a[i]);
        List<Long> pre = new ArrayList<>();
        for (int i = 0; i <= a.length; i++) pre.add(f.prefix(i));
        System.out.println(pre);
        System.out.println(f.rangeSum(2, 6));         // 9 - 3 + 5 + 20
        f.add(3, 10);                                 // a[3] becomes 7
        System.out.println(f.rangeSum(2, 6) + " " + f.prefix(8));
        System.out.println(Arrays.toString(Arrays.copyOfRange(f.t, 1, f.n + 1)));
    }
}
