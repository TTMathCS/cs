import java.util.ArrayList;
import java.util.List;

public class CoinChange {
    static List<Integer> used = new ArrayList<>();

    /** The fewest coins that add up to amount (any coin may be used many times), and which coins; -1 if impossible. */
    static int minCoins(int[] coins, int amount) {
        final int INF = Integer.MAX_VALUE;
        int[] best = new int[amount + 1];             // best[x] = fewest coins for the amount x
        int[] last = new int[amount + 1];             // last[x] = the coin used last in that best way
        for (int x = 1; x <= amount; x++) {
            best[x] = INF;
            for (int c : coins)
                if (c <= x && best[x - c] != INF && best[x - c] + 1 < best[x]) {
                    best[x] = best[x - c] + 1;
                    last[x] = c;
                }
        }
        used = new ArrayList<>();
        if (best[amount] == INF) return -1;
        for (int x = amount; x > 0; x -= last[x]) used.add(last[x]);   // walk back through the choices
        return best[amount];
    }

    /** How many different sets of coins add up to amount (order does not matter). */
    static long countWays(int[] coins, int amount) {
        long[] ways = new long[amount + 1];
        ways[0] = 1;                                  // one way to make 0: no coins
        for (int c : coins)                           // coins in the outer loop, so each set is counted once
            for (int x = c; x <= amount; x++) ways[x] += ways[x - c];
        return ways[amount];
    }

    public static void main(String[] args) {
        int k = minCoins(new int[]{1, 3, 4}, 6);
        System.out.println(k + " " + used);
        k = minCoins(new int[]{1, 5, 10, 25}, 63);
        System.out.println(k + " " + used);
        k = minCoins(new int[]{2}, 3);
        System.out.println(k + " " + used);
        System.out.println(countWays(new int[]{1, 2, 5}, 5) + " " + countWays(new int[]{1, 5, 10, 25}, 100));
    }
}
