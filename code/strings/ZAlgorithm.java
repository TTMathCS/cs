import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class ZAlgorithm {
    /** z[i] = the length of the longest stretch starting at i that equals the start of s (z[0] = len(s)). */
    static int[] zArray(String s) {
        int n = s.length();
        int[] z = new int[n];
        if (n > 0) z[0] = n;
        int l = 0, r = 0;                             // s[l..r) is the rightmost stretch found that equals a prefix
        for (int i = 1; i < n; i++) {
            if (i < r) z[i] = Math.min(r - i, z[i - l]);   // inside a known stretch: reuse the copy's value
            while (i + z[i] < n && s.charAt(z[i]) == s.charAt(i + z[i])) z[i]++;   // then extend directly
            if (i + z[i] > r) { l = i; r = i + z[i]; }
        }
        return z;
    }

    /** Every position where p starts in text: z-values of p + separator + text that reach len(p). */
    static List<Integer> zSearch(String text, String p) {
        int[] z = zArray(p + "\0" + text);
        int m = p.length();
        List<Integer> found = new ArrayList<>();
        for (int i = m + 1; i < z.length; i++) if (z[i] >= m) found.add(i - m - 1);
        return found;
    }

    public static void main(String[] args) {
        System.out.println(Arrays.toString(zArray("aabxaab")));
        System.out.println(Arrays.toString(zArray("aaaaa")));
        System.out.println(zSearch("the red planet has red dust", "red"));
    }
}
