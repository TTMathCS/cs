public class Growth {
    /** Looks at every value once, like finding the largest: n steps. */
    static long linearSteps(int n) {
        long steps = 0;
        for (int i = 0; i < n; i++) steps++;
        return steps;
    }

    /** Halves the range until one value is left, like binary search: about log2(n) steps. */
    static long logSteps(int n) {
        long steps = 0;
        while (n > 1) { n /= 2; steps++; }
        return steps;
    }

    /** Looks at every pair i < j, like checking for duplicates the slow way: n(n-1)/2 steps. */
    static long quadraticSteps(int n) {
        long steps = 0;
        for (int i = 0; i < n; i++)
            for (int j = i + 1; j < n; j++) steps++;
        return steps;
    }

    public static void main(String[] args) {
        System.out.println("n halving linear pairs");
        for (int n : new int[]{10, 100, 1000, 4000})
            System.out.println(n + " " + logSteps(n) + " " + linearSteps(n) + " " + quadraticSteps(n));
    }
}
