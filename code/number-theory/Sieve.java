import java.util.ArrayList;
import java.util.List;

public class Sieve {
    /** Sieve of Eratosthenes: isPrime[k] for every k from 0 to n. */
    static boolean[] sieve(int n) {
        boolean[] isPrime = new boolean[n + 1];
        for (int k = 2; k <= n; k++) isPrime[k] = true;
        for (long p = 2; p * p <= n; p++)
            if (isPrime[(int) p])
                for (long k = p * p; k <= n; k += p) isPrime[(int) k] = false;   // smaller multiples are done
        return isPrime;
    }

    /** spf[k] = the smallest prime that divides k (for k >= 2): factor any k <= n in O(log k) steps. */
    static int[] smallestFactors(int n) {
        int[] spf = new int[n + 1];
        for (int k = 0; k <= n; k++) spf[k] = k;
        for (long p = 2; p * p <= n; p++)
            if (spf[(int) p] == p)                    // p is prime
                for (long k = p * p; k <= n; k += p)
                    if (spf[(int) k] == k) spf[(int) k] = (int) p;
        return spf;
    }

    static List<Integer> factorize(int k, int[] spf) {
        List<Integer> out = new ArrayList<>();
        while (k > 1) { out.add(spf[k]); k /= spf[k]; }
        return out;
    }

    public static void main(String[] args) {
        boolean[] isP = sieve(50);
        List<Integer> primes = new ArrayList<>();
        for (int k = 0; k <= 50; k++) if (isP[k]) primes.add(k);
        System.out.println(primes);
        int count = 0;
        for (boolean b : sieve(1_000_000)) if (b) count++;
        System.out.println(count);
        int[] spf = smallestFactors(10_000);
        System.out.println(factorize(360, spf) + " " + factorize(9973, spf) + " " + factorize(2024, spf));
    }
}
