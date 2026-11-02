import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class NQueens {
    static int n, count;
    static boolean[] cols, diag1, diag2;
    static int[] place, first;

    /** Place n queens on an n x n board so that none attacks another. One queen per row: try each column,
     *  skip columns and diagonals already under attack, and back up when a row has no safe square.
     *  Returns the number of solutions; the first one found is left in first. */
    static int nQueens(int size) {
        n = size; count = 0; first = null;
        cols = new boolean[n]; diag1 = new boolean[2 * n]; diag2 = new boolean[2 * n];
        place = new int[n];
        go(0);
        return count;
    }

    static void go(int r) {
        if (r == n) {
            count++;
            if (first == null) first = place.clone();
            return;
        }
        for (int c = 0; c < n; c++) {
            if (cols[c] || diag1[r + c] || diag2[r - c + n]) continue;   // attacked: prune this branch
            cols[c] = diag1[r + c] = diag2[r - c + n] = true;
            place[r] = c;
            go(r + 1);
            cols[c] = diag1[r + c] = diag2[r - c + n] = false;   // undo, try the next column
        }
    }

    public static void main(String[] args) {
        List<Integer> counts = new ArrayList<>();
        for (int k = 1; k <= 10; k++) counts.add(nQueens(k));
        System.out.println(counts);
        nQueens(8);
        System.out.println(Arrays.toString(first));
        nQueens(6);
        for (int c : first) {
            StringBuilder row = new StringBuilder();
            for (int k = 0; k < 6; k++) row.append(k == c ? 'Q' : '.');
            System.out.println(row);
        }
    }
}
