public class ShipCapacity {
    /** Loads packages in order onto one ship per day; returns how many days that takes. */
    static int daysNeeded(int[] weights, long capacity) {
        int days = 1;
        long load = 0;
        for (int w : weights) {
            if (load + w > capacity) { days++; load = 0; }   // does not fit today: start a new day
            load += w;
        }
        return days;
    }

    /** The smallest ship capacity that moves every package, in order, within d days. */
    static long minCapacity(int[] weights, int d) {
        long lo = 0, hi = 0;
        for (int w : weights) { lo = Math.max(lo, w); hi += w; }   // lo may be too small; hi always works
        while (lo < hi) {
            long mid = (lo + hi) / 2;
            if (daysNeeded(weights, mid) <= d) hi = mid;      // mid works: the answer is mid or smaller
            else lo = mid + 1;                                // mid fails: the answer is bigger
        }
        return lo;
    }

    /** The largest whole number r with r * r <= n. */
    static long isqrt(long n) {
        long lo = 0, hi = Math.min(n, 3037000499L);           // 3037000499^2 still fits in a long
        while (lo < hi) {
            long mid = lo + (hi - lo + 1) / 2;                // round up, so lo = mid makes progress
            if (mid * mid <= n) lo = mid;
            else hi = mid - 1;
        }
        return lo;
    }

    public static void main(String[] args) {
        System.out.println(minCapacity(new int[]{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}, 5));
        System.out.println(minCapacity(new int[]{3, 2, 2, 4, 1, 4}, 3));
        System.out.println(minCapacity(new int[]{1, 2, 3, 1, 1}, 4));
        System.out.println(isqrt(0) + " " + isqrt(15) + " " + isqrt(16) + " " + isqrt(1000000007L));
    }
}
