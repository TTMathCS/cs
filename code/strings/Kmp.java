import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class Kmp {
    /** pi[i] = the length of the longest proper prefix of p[0..i] that is also a suffix of it. */
    static int[] prefixFunction(String p) {
        int[] pi = new int[p.length()];
        int k = 0;                                    // the length of the current matching prefix
        for (int i = 1; i < p.length(); i++) {
            while (k > 0 && p.charAt(i) != p.charAt(k)) k = pi[k - 1];   // fall back to the next shorter border
            if (p.charAt(i) == p.charAt(k)) k++;
            pi[i] = k;
        }
        return pi;
    }

    /** Every position where p starts in text (Knuth-Morris-Pratt), in O(len(text) + len(p)). */
    static List<Integer> kmpSearch(String text, String p) {
        List<Integer> found = new ArrayList<>();
        if (p.isEmpty()) { for (int i = 0; i <= text.length(); i++) found.add(i); return found; }
        int[] pi = prefixFunction(p);
        int k = 0;                                    // how many letters of p match right now
        for (int i = 0; i < text.length(); i++) {
            char ch = text.charAt(i);
            while (k > 0 && ch != p.charAt(k)) k = pi[k - 1];   // never move back in text: shift p using pi
            if (ch == p.charAt(k)) k++;
            if (k == p.length()) {                    // a full match ends at i
                found.add(i - p.length() + 1);
                k = pi[k - 1];                        // keep going, to find overlapping matches too
            }
        }
        return found;
    }

    public static void main(String[] args) {
        System.out.println(Arrays.toString(prefixFunction("ABABCABAB")));
        System.out.println(kmpSearch("ABABDABACDABABCABAB", "ABABCABAB"));
        System.out.println(kmpSearch("AAAAA", "AA") + " " + kmpSearch("olympus mons", "mars"));
    }
}
