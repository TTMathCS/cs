import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class Dfs {
    static List<List<Integer>> adj;
    static boolean[] seen;
    static List<Integer> order;

    /** The order in which depth-first search first visits the vertices reachable from start. */
    static List<Integer> dfsOrder(List<List<Integer>> g, int start) {
        adj = g; seen = new boolean[g.size()]; order = new ArrayList<>();
        visit(start);
        return order;
    }

    static void visit(int u) {
        seen[u] = true;
        order.add(u);
        for (int v : adj.get(u))
            if (!seen[v]) visit(v);                   // go as deep as possible before u's next neighbour
    }

    /** The same order without recursion, using an explicit stack (safe for huge graphs). */
    static List<Integer> dfsIterative(List<List<Integer>> g, int start) {
        boolean[] seen = new boolean[g.size()];
        List<Integer> order = new ArrayList<>();
        ArrayDeque<Integer> stack = new ArrayDeque<>();
        stack.push(start);
        while (!stack.isEmpty()) {
            int u = stack.pop();
            if (seen[u]) continue;
            seen[u] = true;
            order.add(u);
            List<Integer> nb = g.get(u);
            for (int i = nb.size() - 1; i >= 0; i--)  // reversed, so the first neighbour is popped first
                if (!seen[nb.get(i)]) stack.push(nb.get(i));
        }
        return order;
    }

    /** Labels each vertex with the number of its connected component; returns the count. */
    static int components(List<List<Integer>> g, int[] comp) {
        Arrays.fill(comp, -1);
        int count = 0;
        for (int s = 0; s < g.size(); s++) {
            if (comp[s] != -1) continue;              // already labelled
            ArrayDeque<Integer> stack = new ArrayDeque<>();
            stack.push(s);
            comp[s] = count;
            while (!stack.isEmpty()) {
                int u = stack.pop();
                for (int v : g.get(u))
                    if (comp[v] == -1) { comp[v] = count; stack.push(v); }
            }
            count++;
        }
        return count;
    }

    /** Undirected graph: is there a cycle? (An edge to an already-seen vertex other than our parent.) */
    static boolean hasCycle(List<List<Integer>> g) {
        boolean[] seen = new boolean[g.size()];
        for (int s = 0; s < g.size(); s++) {
            if (seen[s]) continue;
            ArrayDeque<int[]> stack = new ArrayDeque<>();
            stack.push(new int[]{s, -1});
            seen[s] = true;
            while (!stack.isEmpty()) {
                int[] top = stack.pop();
                int u = top[0], parent = top[1];
                for (int v : g.get(u)) {
                    if (!seen[v]) { seen[v] = true; stack.push(new int[]{v, u}); }
                    else if (v != parent) return true;
                }
            }
        }
        return false;
    }

    static List<List<Integer>> build(int n, int[][] edges) {
        List<List<Integer>> g = new ArrayList<>();
        for (int i = 0; i < n; i++) g.add(new ArrayList<>());
        for (int[] e : edges) { g.get(e[0]).add(e[1]); g.get(e[1]).add(e[0]); }
        return g;
    }

    static String py(boolean b) { return b ? "True" : "False"; }

    public static void main(String[] args) {
        List<List<Integer>> g = build(8, new int[][]{{0, 1}, {0, 2}, {1, 3}, {2, 3}, {3, 4}, {4, 5}, {2, 5}, {6, 7}});
        System.out.println(dfsOrder(g, 0) + " " + dfsIterative(g, 0));
        int[] comp = new int[8];
        int count = components(g, comp);
        System.out.println("(" + count + ", " + Arrays.toString(comp) + ")");
        List<List<Integer>> tree = build(5, new int[][]{{0, 1}, {0, 2}, {2, 3}, {2, 4}});
        System.out.println(py(hasCycle(g)) + " " + py(hasCycle(tree)));
    }
}
