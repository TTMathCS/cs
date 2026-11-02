public class Lcs {
    static String found = "";

    /** The longest common subsequence of a and b: the longest string whose letters appear in both, in order
     *  (not necessarily next to each other). Returns its length; one such string is left in found. */
    static int lcs(String a, String b) {
        int n = a.length(), m = b.length();
        int[][] L = new int[n + 1][m + 1];            // L[i][j] = LCS length of a[:i] and b[:j]
        for (int i = 1; i <= n; i++)
            for (int j = 1; j <= m; j++)
                if (a.charAt(i - 1) == b.charAt(j - 1)) L[i][j] = L[i - 1][j - 1] + 1;   // last letters match
                else L[i][j] = Math.max(L[i - 1][j], L[i][j - 1]);   // drop the last letter of a, or of b
        StringBuilder out = new StringBuilder();
        int i = n, j = m;
        while (i > 0 && j > 0) {                      // walk back from the corner
            if (a.charAt(i - 1) == b.charAt(j - 1)) { out.append(a.charAt(i - 1)); i--; j--; }
            else if (L[i - 1][j] >= L[i][j - 1]) i--;
            else j--;
        }
        found = out.reverse().toString();
        return L[n][m];
    }

    public static void main(String[] args) {
        String[][] pairs = {{"ABCBDAB", "BDCABA"}, {"AGGTAB", "GXTXAYB"}, {"OLYMPUS", "ELYSIUM"}};
        for (String[] p : pairs) {
            int k = lcs(p[0], p[1]);
            System.out.println(k + " " + found);
        }
    }
}
