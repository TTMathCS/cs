public class Gcd {
    /** Euclid's algorithm: gcd(a, b) = gcd(b, a mod b), until the second number is 0. */
    static long gcd(long a, long b) {
        while (b != 0) { long t = a % b; a = b; b = t; }
        return a;
    }

    /** Extended Euclid: returns {g, x, y} with a*x + b*y = g = gcd(a, b). */
    static long[] extGcd(long a, long b) {
        if (b == 0) return new long[]{a, 1, 0};
        long[] r = extGcd(b, a % b);                  // b*x1 + (a mod b)*y1 = g
        return new long[]{r[0], r[2], r[1] - (a / b) * r[2]};   // rewrite a mod b as a - (a / b)*b
    }

    static long lcm(long a, long b) {
        return a / gcd(a, b) * b;                     // divide first, so the product does not grow too big
    }

    /** The x with a*x = 1 (mod m), or -1 if there is none (when gcd(a, m) > 1). */
    static long modInverse(long a, long m) {
        long[] r = extGcd(a, m);
        return r[0] == 1 ? ((r[1] % m) + m) % m : -1;
    }

    public static void main(String[] args) {
        System.out.println(gcd(1071, 462) + " " + gcd(462, 1071) + " " + gcd(17, 5) + " " + gcd(0, 9));
        long[] e = extGcd(240, 46);
        System.out.println(e[0] + " " + e[1] + " " + e[2]);
        System.out.println(lcm(4, 6) + " " + lcm(687, 365));
        System.out.println(modInverse(3, 11) + " " + modInverse(10, 17) + " " + modInverse(6, 9));
    }
}
