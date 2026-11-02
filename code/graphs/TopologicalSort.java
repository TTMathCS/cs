import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class TopologicalSort {
    /** Topological order of a directed graph (Kahn's algorithm), or null if it has a cycle. */
    static List<Integer> kahn(int n, int[][] edges) {
        List<List<Integer>> adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        int[] indeg = new int[n];                     // how many arrows point into each vertex
        for (int[] e : edges) { adj.get(e[0]).add(e[1]); indeg[e[1]]++; }
        ArrayDeque<Integer> q = new ArrayDeque<>();
        for (int v = 0; v < n; v++) if (indeg[v] == 0) q.add(v);   // nothing has to come before these
        List<Integer> order = new ArrayList<>();
        while (!q.isEmpty()) {
            int u = q.poll();
            order.add(u);
            for (int v : adj.get(u))                  // "remove" u: its arrows no longer count
                if (--indeg[v] == 0) q.add(v);
        }
        return order.size() == n ? order : null;      // leftovers lie on a cycle
    }

    static List<List<Integer>> g;
    static int[] state;                               // 0 = new, 1 = on the current path, 2 = finished
    static List<Integer> finished;

    /** Topological order by depth-first search: a vertex is finished after everything it points to. */
    static List<Integer> dfsTopo(int n, int[][] edges) {
        g = new ArrayList<>();
        for (int i = 0; i < n; i++) g.add(new ArrayList<>());
        for (int[] e : edges) g.get(e[0]).add(e[1]);
        state = new int[n];
        finished = new ArrayList<>();
        for (int u = 0; u < n; u++) if (state[u] == 0) visit(u);
        Collections.reverse(finished);                // reverse finishing order
        return finished;
    }

    static void visit(int u) {
        state[u] = 1;
        for (int v : g.get(u)) {
            if (state[v] == 1) throw new IllegalStateException("cycle");   // an arrow back into the path
            if (state[v] == 0) visit(v);
        }
        state[u] = 2;
        finished.add(u);
    }

    public static void main(String[] args) {
        // 0 maths, 1 programming, 2 data structures, 3 algorithms, 4 databases, 5 machine learning
        int[][] edges = {{0, 3}, {1, 2}, {2, 3}, {2, 4}, {3, 5}, {0, 5}};
        System.out.println(kahn(6, edges));
        System.out.println(dfsTopo(6, edges));
        List<Integer> cyc = kahn(3, new int[][]{{0, 1}, {1, 2}, {2, 0}});
        System.out.println(cyc == null ? "None" : cyc.toString());
    }
}
