import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.List;

public class Kruskal {
    static int[] parent;

    static int find(int x) {                          // union-find with path halving
        while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; }
        return x;
    }

    /** Minimum spanning tree of a connected undirected graph; returns its weight and adds its edges to chosen. */
    static int kruskal(int n, int[][] edges, List<int[]> chosen) {
        parent = new int[n];
        for (int i = 0; i < n; i++) parent[i] = i;
        int[][] sorted = edges.clone();               // cheapest edges first (ties by u, then v)
        Arrays.sort(sorted, Comparator.<int[]>comparingInt(e -> e[2]).thenComparingInt(e -> e[0]).thenComparingInt(e -> e[1]));
        int total = 0;
        for (int[] e : sorted) {
            int ru = find(e[0]), rv = find(e[1]);
            if (ru != rv) {                           // joins two different trees: keep it
                parent[ru] = rv;
                total += e[2];
                chosen.add(e);
                if (chosen.size() == n - 1) break;
            }                                         // otherwise it would close a cycle: skip it
        }
        return total;
    }

    public static void main(String[] args) {
        int[][] edges = {{0, 1, 4}, {0, 7, 8}, {1, 2, 8}, {1, 7, 11}, {2, 3, 7}, {2, 8, 2}, {2, 5, 4}, {3, 4, 9},
            {3, 5, 14}, {4, 5, 10}, {5, 6, 2}, {6, 7, 1}, {6, 8, 6}, {7, 8, 7}};
        List<int[]> chosen = new ArrayList<>();
        System.out.println(kruskal(9, edges, chosen));
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < chosen.size(); i++) {
            int[] e = chosen.get(i);
            sb.append(i > 0 ? ", " : "").append("(").append(e[0]).append(", ").append(e[1]).append(", ").append(e[2]).append(")");
        }
        System.out.println(sb.append("]"));
    }
}
