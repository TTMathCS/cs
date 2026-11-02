import java.util.ArrayList;
import java.util.List;
import java.util.PriorityQueue;

public class Prim {
    /** Minimum spanning tree by growing one tree from start; returns its weight, fills chosen in order. */
    static int prim(int n, int[][] edges, int start, List<int[]> chosen) {
        List<List<int[]>> adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        for (int[] e : edges) { adj.get(e[0]).add(new int[]{e[2], e[1]}); adj.get(e[1]).add(new int[]{e[2], e[0]}); }
        boolean[] inTree = new boolean[n];
        // (edge weight, vertex, the tree vertex it hangs from); ties broken like Python's tuples
        PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) ->
            a[0] != b[0] ? Integer.compare(a[0], b[0]) : a[1] != b[1] ? Integer.compare(a[1], b[1]) : Integer.compare(a[2], b[2]));
        pq.add(new int[]{0, start, -1});
        int total = 0;
        while (!pq.isEmpty()) {
            int[] top = pq.poll();                    // the cheapest edge leaving the tree
            int w = top[0], v = top[1], from = top[2];
            if (inTree[v]) continue;                  // both ends already in the tree: skip
            inTree[v] = true;
            total += w;
            if (from != -1) chosen.add(new int[]{from, v, w});
            for (int[] e : adj.get(v))
                if (!inTree[e[1]]) pq.add(new int[]{e[0], e[1], v});
        }
        return total;
    }

    public static void main(String[] args) {
        int[][] edges = {{0, 1, 4}, {0, 7, 8}, {1, 2, 8}, {1, 7, 11}, {2, 3, 7}, {2, 8, 2}, {2, 5, 4}, {3, 4, 9},
            {3, 5, 14}, {4, 5, 10}, {5, 6, 2}, {6, 7, 1}, {6, 8, 6}, {7, 8, 7}};
        List<int[]> chosen = new ArrayList<>();
        System.out.println(prim(9, edges, 0, chosen));
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < chosen.size(); i++) {
            int[] e = chosen.get(i);
            sb.append(i > 0 ? ", " : "").append("(").append(e[0]).append(", ").append(e[1]).append(", ").append(e[2]).append(")");
        }
        System.out.println(sb.append("]"));
    }
}
