import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.PriorityQueue;

public class Dijkstra {
    static final String[] PLACES = {"Erebus Montes", "Olympus Mons", "Ascraeus Mons", "Valles Marineris",
        "Elysium Mons", "Utopia Planitia", "Gale crater", "Jezero crater", "Hellas Planitia"};
    // roads between real places on Mars, with their great-circle lengths in km
    static final int[][] ROADS = {{0, 1, 2369}, {0, 4, 2016}, {0, 5, 2305}, {1, 2, 1740}, {2, 3, 3043},
        {4, 6, 1879}, {5, 4, 1486}, {5, 7, 3214}, {7, 6, 3782}, {7, 8, 3616}, {6, 8, 4122}, {1, 6, 5337}};

    /** Shortest distances from src when every edge weight is >= 0; fills parent[]. */
    static long[] dijkstra(List<List<int[]>> adj, int src, int[] parent) {
        long[] dist = new long[adj.size()];
        Arrays.fill(dist, Long.MAX_VALUE);
        Arrays.fill(parent, -1);
        dist[src] = 0;
        PriorityQueue<long[]> pq = new PriorityQueue<>((a, b) -> Long.compare(a[0], b[0]));
        pq.add(new long[]{0, src});                   // (distance found so far, vertex)
        while (!pq.isEmpty()) {
            long[] top = pq.poll();                   // the closest vertex not yet settled
            long d = top[0];
            int u = (int) top[1];
            if (d > dist[u]) continue;                // an old, longer entry: skip it
            for (int[] e : adj.get(u)) {
                int v = e[0], w = e[1];
                if (d + w < dist[v]) {                // relax: going through u is shorter
                    dist[v] = d + w;
                    parent[v] = u;
                    pq.add(new long[]{dist[v], v});
                }
            }
        }
        return dist;
    }

    static List<Integer> route(int[] parent, int t) {
        List<Integer> out = new ArrayList<>();
        for (; t != -1; t = parent[t]) out.add(t);
        Collections.reverse(out);
        return out;
    }

    public static void main(String[] args) {
        List<List<int[]>> adj = new ArrayList<>();
        for (int i = 0; i < PLACES.length; i++) adj.add(new ArrayList<>());
        for (int[] r : ROADS) { adj.get(r[0]).add(new int[]{r[1], r[2]}); adj.get(r[1]).add(new int[]{r[0], r[2]}); }
        int[] parent = new int[PLACES.length];
        long[] dist = dijkstra(adj, 0, parent);
        for (int v = 0; v < PLACES.length; v++) {
            List<String> names = new ArrayList<>();
            for (int x : route(parent, v)) names.add(PLACES[x]);
            System.out.println(PLACES[v] + ": " + dist[v] + " km via " + String.join(" > ", names));
        }
    }
}
