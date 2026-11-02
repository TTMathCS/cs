import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class Scc {
    static List<List<Integer>> adj, radj;
    static boolean[] seen;
    static List<Integer> order;
    static int[] comp;

    /** Strongly connected components (Kosaraju); returns the count and fills comp, numbered in topological order. */
    static int kosaraju(int n, int[][] edges) {
        adj = new ArrayList<>(); radj = new ArrayList<>();   // radj: every arrow reversed
        for (int i = 0; i < n; i++) { adj.add(new ArrayList<>()); radj.add(new ArrayList<>()); }
        for (int[] e : edges) { adj.get(e[0]).add(e[1]); radj.get(e[1]).add(e[0]); }
        seen = new boolean[n];
        order = new ArrayList<>();
        for (int u = 0; u < n; u++) if (!seen[u]) dfs1(u);
        comp = new int[n];
        Arrays.fill(comp, -1);
        int c = 0;
        for (int i = n - 1; i >= 0; i--) {            // pass 2: latest finisher first, on the reversed graph
            int u = order.get(i);
            if (comp[u] == -1) dfs2(u, c++);
        }
        return c;
    }

    static void dfs1(int u) {                         // pass 1: record finishing order
        seen[u] = true;
        for (int v : adj.get(u)) if (!seen[v]) dfs1(v);
        order.add(u);
    }

    static void dfs2(int u, int c) {
        comp[u] = c;
        for (int v : radj.get(u)) if (comp[v] == -1) dfs2(v, c);
    }

    public static void main(String[] args) {
        int[][] edges = {{0, 1}, {1, 2}, {2, 0}, {2, 3}, {3, 4}, {4, 5}, {5, 3}, {6, 5}, {6, 7}, {7, 6}};
        int count = kosaraju(8, edges);
        System.out.println(count + " " + Arrays.toString(comp));
        List<List<Integer>> groups = new ArrayList<>();
        for (int c = 0; c < count; c++) {
            List<Integer> g = new ArrayList<>();
            for (int v = 0; v < 8; v++) if (comp[v] == c) g.add(v);
            groups.add(g);
        }
        System.out.println(groups);
    }
}
