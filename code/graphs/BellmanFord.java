import java.util.Arrays;

public class BellmanFord {
    static final long INF = Long.MAX_VALUE;

    /** Shortest distances from src even with negative edge weights, or null if a negative cycle is reachable. */
    static long[] bellmanFord(int n, int[][] edges, int src) {
        long[] dist = new long[n];
        Arrays.fill(dist, INF);
        dist[src] = 0;
        for (int round = 0; round < n - 1; round++) { // a shortest path uses at most n-1 edges
            boolean changed = false;
            for (int[] e : edges) {
                int u = e[0], v = e[1], w = e[2];
                if (dist[u] != INF && dist[u] + w < dist[v]) { dist[v] = dist[u] + w; changed = true; }
            }
            if (!changed) break;                      // nothing improved: we are done early
        }
        for (int[] e : edges)                         // one more round: any improvement means a negative cycle
            if (dist[e[0]] != INF && dist[e[0]] + e[2] < dist[e[1]]) return null;
        return dist;
    }

    static String show(long[] dist) {
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < dist.length; i++) sb.append(i > 0 ? ", " : "").append(dist[i] == INF ? "inf" : String.valueOf(dist[i]));
        return sb.append("]").toString();
    }

    public static void main(String[] args) {
        int[][] edges = {{0, 1, 6}, {0, 2, 7}, {1, 2, 8}, {1, 3, 5}, {1, 4, -4}, {2, 3, -3}, {2, 4, 9}, {3, 1, -2},
            {4, 0, 2}, {4, 3, 7}};
        System.out.println(show(bellmanFord(5, edges, 0)));
        System.out.println(show(bellmanFord(6, edges, 0)));   // vertex 5 has no edges: unreachable
        int[][] bad = {{0, 1, 1}, {1, 2, -1}, {2, 1, -1}, {2, 3, 1}};
        System.out.println(bellmanFord(4, bad, 0) == null ? "True" : "False");
    }
}
