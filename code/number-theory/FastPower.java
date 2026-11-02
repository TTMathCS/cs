public class FastPower {
    /** a to the power n with O(log n) multiplications (square and multiply). */
    static long power(long a, long n) {
        long result = 1;
        while (n > 0) {
            if ((n & 1) == 1) result *= a;            // this binary digit of n is 1: include the current square
            a *= a;                                   // a, a^2, a^4, a^8, ...
            n >>= 1;
        }
        return result;
    }

    /** a^n mod m, keeping every number below m. */
    static long powerMod(long a, long n, long m) {
        long result = 1 % m;
        a %= m;
        while (n > 0) {
            if ((n & 1) == 1) result = result * a % m;
            a = a * a % m;
            n >>= 1;
        }
        return result;
    }

    static long[][] matMult(long[][] X, long[][] Y) {
        return new long[][]{
            {X[0][0] * Y[0][0] + X[0][1] * Y[1][0], X[0][0] * Y[0][1] + X[0][1] * Y[1][1]},
            {X[1][0] * Y[0][0] + X[1][1] * Y[1][0], X[1][0] * Y[0][1] + X[1][1] * Y[1][1]}};
    }

    /** The nth Fibonacci number from the matrix [[1, 1], [1, 0]] to the power n. */
    static long fib(int n) {
        long[][] result = {{1, 0}, {0, 1}}, M = {{1, 1}, {1, 0}};
        while (n > 0) {
            if ((n & 1) == 1) result = matMult(result, M);
            n >>= 1;
            if (n > 0) M = matMult(M, M);             // skip the last squaring, which would overflow
        }
        return result[0][1];
    }

    public static void main(String[] args) {
        System.out.println(power(2, 10) + " " + power(3, 13) + " " + power(7, 0));
        final long MOD = 1_000_000_007L;
        System.out.println(powerMod(2, 1_000_000, MOD) + " " + powerMod(3, MOD - 2, MOD) * 3 % MOD);
        System.out.println(powerMod(5, 117, 19) + " " + fib(10) + " " + fib(90));
    }
}
