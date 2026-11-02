import java.util.Arrays;

public class FloydWarshall {
    static final int INF = Integer.MAX_VALUE / 2;     // half, so INF + INF does not overflow

    /** All-pairs shortest distances. d[i][j] is the edge weight (INF if none, 0 on the diagonal). */
    static void floydWarshall(int[][] d) {
        int n = d.length;
        for (int k = 0; k < n; k++)                   // allow k as a stop in the middle of paths
            for (int i = 0; i < n; i++)
                for (int j = 0; j < n; j++)
                    if (d[i][k] + d[k][j] < d[i][j]) d[i][j] = d[i][k] + d[k][j];
    }

    public static void main(String[] args) {
        int[][] d = {{0, 3, INF, 7}, {8, 0, 2, INF}, {5, INF, 0, 1}, {2, INF, INF, 0}};
        floydWarshall(d);
        for (int[] row : d) System.out.println(Arrays.toString(row));
        boolean neg = false;
        for (int i = 0; i < d.length; i++) neg |= d[i][i] < 0;   // a negative diagonal: a negative cycle
        System.out.println(neg ? "True" : "False");
    }
}
