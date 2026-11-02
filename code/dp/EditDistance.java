import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class EditDistance {
    static List<String> steps = new ArrayList<>();

    /** The fewest single-letter inserts, deletes and replacements that turn a into b (Levenshtein distance).
     *  Returns the distance; the list of steps is left in steps. */
    static int editDistance(String a, String b) {
        int n = a.length(), m = b.length();
        int[][] D = new int[n + 1][m + 1];            // D[i][j] = distance from a[:i] to b[:j]
        for (int i = 0; i <= n; i++) D[i][0] = i;     // delete all i letters
        for (int j = 0; j <= m; j++) D[0][j] = j;     // insert all j letters
        for (int i = 1; i <= n; i++)
            for (int j = 1; j <= m; j++) {
                int same = a.charAt(i - 1) == b.charAt(j - 1) ? 0 : 1;
                D[i][j] = Math.min(Math.min(D[i - 1][j] + 1,    // delete a[i-1]
                                            D[i][j - 1] + 1),   // insert b[j-1]
                                   D[i - 1][j - 1] + same);     // keep or replace
            }
        steps = new ArrayList<>();
        int i = n, j = m;
        while (i > 0 || j > 0) {                      // walk back to list the steps
            if (i > 0 && j > 0 && D[i][j] == D[i - 1][j - 1] + (a.charAt(i - 1) != b.charAt(j - 1) ? 1 : 0)) {
                if (a.charAt(i - 1) != b.charAt(j - 1)) steps.add("replace " + a.charAt(i - 1) + " with " + b.charAt(j - 1));
                i--; j--;
            } else if (i > 0 && D[i][j] == D[i - 1][j] + 1) {
                steps.add("delete " + a.charAt(i - 1)); i--;
            } else {
                steps.add("insert " + b.charAt(j - 1)); j--;
            }
        }
        Collections.reverse(steps);
        return D[n][m];
    }

    public static void main(String[] args) {
        String[][] pairs = {{"kitten", "sitting"}, {"sunday", "saturday"}, {"mars", "stars"}};
        for (String[] p : pairs) {
            int d = editDistance(p[0], p[1]);
            System.out.println(p[0] + " " + p[1] + " " + d + " " + String.join("; ", steps));
        }
    }
}
