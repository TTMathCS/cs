import java.util.ArrayList;
import java.util.List;

public class Fibonacci {
    static long calls = 0;

    /** Straight from the definition: exponential time, because the same values are worked out again and again. */
    static long fibNaive(int n) {
        calls++;
        return n < 2 ? n : fibNaive(n - 1) + fibNaive(n - 2);
    }

    static long[] memo = new long[100];

    /** Top-down: the same recursion, but each answer is remembered the first time (memoization). */
    static long fibMemo(int n) {
        if (n < 2) return n;
        if (memo[n] != 0) return memo[n];
        return memo[n] = fibMemo(n - 1) + fibMemo(n - 2);
    }

    /** Bottom-up: fill a table from the smallest case upwards (tabulation). */
    static long fibTable(int n) {
        long[] f = new long[n + 1];
        if (n > 0) f[1] = 1;
        for (int i = 2; i <= n; i++) f[i] = f[i - 1] + f[i - 2];
        return f[n];
    }

    /** Bottom-up with only the last two values kept: O(1) memory. */
    static long fibTwo(int n) {
        long a = 0, b = 1;                            // F(i), F(i+1)
        for (int i = 0; i < n; i++) { long t = a + b; a = b; b = t; }
        return a;
    }

    public static void main(String[] args) {
        long f20 = fibNaive(20);
        System.out.println(f20 + " " + calls);
        System.out.println(fibMemo(50) + " " + fibTable(50) + " " + fibTwo(50));
        List<Long> first = new ArrayList<>();
        for (int i = 0; i <= 10; i++) first.add(fibTwo(i));
        System.out.println(first);
    }
}
