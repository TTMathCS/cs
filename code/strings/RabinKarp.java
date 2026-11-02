import java.util.ArrayList;
import java.util.List;

public class RabinKarp {
    static int falseAlarms;

    /** Every position where p starts in text, comparing rolling hashes first and letters only when the hashes
     *  agree. The number of false alarms (equal hashes, different letters) is left in falseAlarms. */
    static List<Integer> rabinKarp(String text, String p, long mod, long base) {
        int n = text.length(), m = p.length();
        List<Integer> found = new ArrayList<>();
        falseAlarms = 0;
        if (m > n) return found;
        long high = 1;                                // the weight of the window's first letter: base^(m-1) mod
        for (int i = 0; i < m - 1; i++) high = high * base % mod;
        long hp = 0, ht = 0;
        for (int i = 0; i < m; i++) {                 // hash of p and of the first window
            hp = (hp * base + p.charAt(i)) % mod;
            ht = (ht * base + text.charAt(i)) % mod;
        }
        for (int s = 0; s + m <= n; s++) {
            if (hp == ht) {
                if (text.regionMatches(s, p, 0, m)) found.add(s);   // equal hashes do not prove a match
                else falseAlarms++;
            }
            if (s + m < n) {                          // roll: drop text[s], add text[s+m]
                ht = (ht - text.charAt(s) * high % mod + mod) % mod;
                ht = (ht * base + text.charAt(s + m)) % mod;
            }
        }
        return found;
    }

    public static void main(String[] args) {
        String text = "dust storms on mars can cover all of mars for months";
        List<Integer> f = rabinKarp(text, "mars", 1_000_000_007L, 256);
        System.out.println(f + " " + falseAlarms);
        f = rabinKarp(text, "mars", 13, 256);
        System.out.println(f + " " + falseAlarms);
        f = rabinKarp("abracadabra", "abra", 1_000_000_007L, 256);
        System.out.println(f + " " + falseAlarms);
    }
}
